from decimal import Decimal

from sqlalchemy.orm import Session

from app.exceptions import ConflictError, NotFoundError, SubLedgerError
from app.models.customer import Customer
from app.models.enums import (
    InvoiceStatus,
    LedgerEntryType,
    PaymentStatus,
    SubscriptionStatus,
)
from app.models.invoice import Invoice
from app.models.payment_attempt import PaymentAttempt
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.repositories import (
    CustomerRepository,
    InvoiceRepository,
    LedgerRepository,
    PaymentAttemptRepository,
    PlanRepository,
    SubscriptionRepository,
)
from app.schemas.customer import CustomerCreate
from app.schemas.invoice import InvoiceGenerateRequest
from app.schemas.payment import PaymentCreate
from app.schemas.plan import PlanCreate, PlanUpdate


def _billing_period_end(start, billing_cycle: str):
    from datetime import timedelta

    if billing_cycle == "yearly":
        return start + timedelta(days=365)
    if billing_cycle == "quarterly":
        return start + timedelta(days=90)
    return start + timedelta(days=30)


class LedgerService:
    def __init__(self, ledger_repo: LedgerRepository):
        self.ledger_repo = ledger_repo

    def record_invoice_created(self, invoice: Invoice) -> None:
        from app.models.ledger_entry import LedgerEntry

        entry = LedgerEntry(
            customer_id=invoice.customer_id,
            invoice_id=invoice.id,
            entry_type=LedgerEntryType.INVOICE_CREATED.value,
            amount=invoice.amount_due,
            currency=invoice.currency,
            reference_id=invoice.id,
            description=f"Invoice #{invoice.id} created",
        )
        self.ledger_repo.create(entry)

    def record_payment_success(self, payment: PaymentAttempt, invoice: Invoice) -> None:
        from app.models.ledger_entry import LedgerEntry

        entry = LedgerEntry(
            customer_id=invoice.customer_id,
            invoice_id=invoice.id,
            entry_type=LedgerEntryType.PAYMENT_SUCCESS.value,
            amount=payment.amount,
            currency=payment.currency,
            reference_id=payment.id,
            description=f"Payment #{payment.id} succeeded for invoice #{invoice.id}",
        )
        self.ledger_repo.create(entry)

    def record_payment_failure(self, payment: PaymentAttempt, invoice: Invoice) -> None:
        from app.models.ledger_entry import LedgerEntry

        reason = payment.failure_reason or "unknown"
        entry = LedgerEntry(
            customer_id=invoice.customer_id,
            invoice_id=invoice.id,
            entry_type=LedgerEntryType.PAYMENT_FAILURE.value,
            amount=payment.amount,
            currency=payment.currency,
            reference_id=payment.id,
            description=f"Payment #{payment.id} failed: {reason}",
        )
        self.ledger_repo.create(entry)

    def get_customer_ledger(self, customer_id: int) -> list:
        return self.ledger_repo.list_by_customer(customer_id)


class PlanService:
    def __init__(self, plan_repo: PlanRepository):
        self.plan_repo = plan_repo

    def create_plan(self, data: PlanCreate) -> Plan:
        if data.price <= 0:
            raise SubLedgerError("Plan price must be greater than 0")

        plan = Plan(
            name=data.name,
            description=data.description,
            billing_cycle=data.billing_cycle,
            price=data.price,
            currency=data.currency,
            notes=data.notes,
            is_active=True,
        )
        return self.plan_repo.create(plan)

    def get_plan(self, plan_id: int) -> Plan:
        plan = self.plan_repo.get_by_id(plan_id)
        if not plan:
            raise NotFoundError(f"Plan {plan_id} not found")
        return plan

    def list_plans(self) -> list[Plan]:
        return self.plan_repo.list_all()

    def update_plan(self, plan_id: int, data: PlanUpdate) -> Plan:
        plan = self.get_plan(plan_id)

        if data.price is not None and data.price <= 0:
            raise SubLedgerError("Plan price must be greater than 0")

        if data.name is not None:
            plan.name = data.name
        if data.description is not None:
            plan.description = data.description
        if data.billing_cycle is not None:
            plan.billing_cycle = data.billing_cycle
        if data.price is not None:
            plan.price = data.price
        if data.currency is not None:
            plan.currency = data.currency
        if data.notes is not None:
            plan.notes = data.notes
        if data.is_active is not None:
            plan.is_active = data.is_active

        return self.plan_repo.update(plan)


class CustomerService:
    def __init__(self, customer_repo: CustomerRepository):
        self.customer_repo = customer_repo

    def create_customer(self, data: CustomerCreate) -> Customer:
        existing = self.customer_repo.get_by_email(data.email)
        if existing:
            raise ConflictError("Customer email must be unique")

        customer = Customer(
            name=data.name,
            email=data.email,
            company_name=data.company_name,
            status="active",
        )
        return self.customer_repo.create(customer)

    def get_customer(self, customer_id: int) -> Customer:
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise NotFoundError(f"Customer {customer_id} not found")
        return customer

    def list_customers(self) -> list[Customer]:
        return self.customer_repo.list_all()


class SubscriptionService:
    def __init__(
        self,
        subscription_repo: SubscriptionRepository,
        plan_repo: PlanRepository,
        customer_repo: CustomerRepository,
    ):
        self.subscription_repo = subscription_repo
        self.plan_repo = plan_repo
        self.customer_repo = customer_repo

    def create_subscription(self, customer_id: int, plan_id: int) -> Subscription:
        from datetime import datetime, timezone

        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise NotFoundError(f"Customer {customer_id} not found")

        plan = self.plan_repo.get_by_id(plan_id)
        if not plan:
            raise NotFoundError(f"Plan {plan_id} not found")

        if not plan.is_active:
            raise SubLedgerError("A subscription cannot be created for an inactive plan")

        if self.subscription_repo.has_active_for_plan(customer_id, plan_id):
            raise SubLedgerError(
                "Customer cannot have two active subscriptions to the same plan"
            )

        now = datetime.now(timezone.utc)
        period_end = _billing_period_end(now, plan.billing_cycle)

        subscription = Subscription(
            customer_id=customer_id,
            plan_id=plan_id,
            status=SubscriptionStatus.ACTIVE.value,
            start_date=now,
            current_period_start=now,
            current_period_end=period_end,
        )
        return self.subscription_repo.create(subscription)

    def list_subscriptions(self) -> list[Subscription]:
        return self.subscription_repo.list_all()

    def get_subscription(self, subscription_id: int) -> Subscription:
        subscription = self.subscription_repo.get_by_id(subscription_id)
        if not subscription:
            raise NotFoundError(f"Subscription {subscription_id} not found")
        return subscription

    def cancel_subscription(self, subscription_id: int) -> Subscription:
        from datetime import datetime, timezone

        subscription = self.get_subscription(subscription_id)
        if subscription.status == SubscriptionStatus.CANCELLED.value:
            raise SubLedgerError("Subscription is already cancelled")

        subscription.status = SubscriptionStatus.CANCELLED.value
        subscription.cancelled_at = datetime.now(timezone.utc)
        return self.subscription_repo.update(subscription)


class InvoiceService:
    def __init__(
        self,
        subscription_repo: SubscriptionRepository,
        plan_repo: PlanRepository,
        invoice_repo: InvoiceRepository,
        ledger_service: LedgerService,
    ):
        self.subscription_repo = subscription_repo
        self.plan_repo = plan_repo
        self.invoice_repo = invoice_repo
        self.ledger_service = ledger_service

    def generate_invoice(self, data: InvoiceGenerateRequest) -> Invoice:
        from datetime import datetime, timezone

        subscription = self.subscription_repo.get_by_id(data.subscription_id)
        if not subscription:
            raise NotFoundError(f"Subscription {data.subscription_id} not found")

        if subscription.status != SubscriptionStatus.ACTIVE.value:
            raise SubLedgerError("Invoice can only be generated for an active subscription")

        plan = self.plan_repo.get_by_id(subscription.plan_id)
        if not plan:
            raise NotFoundError(f"Plan {subscription.plan_id} not found")

        period_start = data.period_start or subscription.current_period_start
        period_end = data.period_end or subscription.current_period_end
        due_date = period_end

        invoice = Invoice(
            subscription_id=subscription.id,
            customer_id=subscription.customer_id,
            amount_due=plan.price,
            amount_paid=Decimal("0"),
            currency=plan.currency,
            status=InvoiceStatus.ISSUED.value,
            period_start=period_start,
            period_end=period_end,
            due_date=due_date,
        )
        invoice = self.invoice_repo.create(invoice)
        self.ledger_service.record_invoice_created(invoice)
        return invoice

    def get_invoice(self, invoice_id: int) -> Invoice:
        invoice = self.invoice_repo.get_by_id(invoice_id)
        if not invoice:
            raise NotFoundError(f"Invoice {invoice_id} not found")
        return invoice


class PaymentService:
    def __init__(
        self,
        invoice_repo: InvoiceRepository,
        payment_attempt_repo: PaymentAttemptRepository,
        ledger_service: LedgerService,
    ):
        self.invoice_repo = invoice_repo
        self.payment_attempt_repo = payment_attempt_repo
        self.ledger_service = ledger_service

    def record_payment(self, data: PaymentCreate) -> tuple[PaymentAttempt, Invoice]:
        invoice = self.invoice_repo.get_by_id(data.invoice_id)
        if not invoice:
            raise NotFoundError(f"Invoice {data.invoice_id} not found")

        if data.currency != invoice.currency:
            raise SubLedgerError("Payment currency must match invoice currency")

        if invoice.status in (InvoiceStatus.PAID.value, InvoiceStatus.VOID.value):
            raise SubLedgerError(f"Cannot record payment for invoice in {invoice.status} status")

        remaining = invoice.amount_due - invoice.amount_paid

        if data.status == PaymentStatus.SUCCESS and data.amount > remaining:
            raise SubLedgerError(
                "A successful payment cannot exceed the remaining unpaid amount on the invoice"
            )

        payment = PaymentAttempt(
            invoice_id=invoice.id,
            amount=data.amount,
            currency=data.currency,
            status=data.status.value,
            provider_reference=data.provider_reference,
            failure_reason=data.failure_reason,
        )
        payment = self.payment_attempt_repo.create(payment)

        if data.status == PaymentStatus.SUCCESS:
            invoice.amount_paid += data.amount
            if invoice.amount_paid >= invoice.amount_due:
                invoice.status = InvoiceStatus.PAID.value
            else:
                invoice.status = InvoiceStatus.PARTIALLY_PAID.value
            self.invoice_repo.update(invoice)
            self.ledger_service.record_payment_success(payment, invoice)
        else:
            self.ledger_service.record_payment_failure(payment, invoice)

        return payment, invoice


def build_services(db: Session) -> dict:
    plan_repo = PlanRepository(db)
    customer_repo = CustomerRepository(db)
    subscription_repo = SubscriptionRepository(db)
    invoice_repo = InvoiceRepository(db)
    payment_repo = PaymentAttemptRepository(db)
    ledger_repo = LedgerRepository(db)

    ledger_service = LedgerService(ledger_repo)

    return {
        "plan": PlanService(plan_repo),
        "customer": CustomerService(customer_repo),
        "subscription": SubscriptionService(subscription_repo, plan_repo, customer_repo),
        "invoice": InvoiceService(subscription_repo, plan_repo, invoice_repo, ledger_service),
        "payment": PaymentService(invoice_repo, payment_repo, ledger_service),
        "ledger": ledger_service,
    }
