from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.invoice import Invoice
from app.models.ledger_entry import LedgerEntry
from app.models.payment_attempt import PaymentAttempt
from app.models.plan import Plan
from app.models.subscription import Subscription


class PlanRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, plan: Plan) -> Plan:
        self.db.add(plan)
        self.db.flush()
        return plan

    def get_by_id(self, plan_id: int) -> Plan | None:
        return self.db.get(Plan, plan_id)

    def list_all(self) -> list[Plan]:
        return self.db.query(Plan).order_by(Plan.id).all()

    def update(self, plan: Plan) -> Plan:
        self.db.flush()
        return plan


class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, customer: Customer) -> Customer:
        self.db.add(customer)
        self.db.flush()
        return customer

    def get_by_id(self, customer_id: int) -> Customer | None:
        return self.db.get(Customer, customer_id)

    def get_by_email(self, email: str) -> Customer | None:
        return self.db.query(Customer).filter(Customer.email == email).first()

    def list_all(self) -> list[Customer]:
        return self.db.query(Customer).order_by(Customer.id).all()


class SubscriptionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, subscription: Subscription) -> Subscription:
        self.db.add(subscription)
        self.db.flush()
        return subscription

    def get_by_id(self, subscription_id: int) -> Subscription | None:
        return self.db.get(Subscription, subscription_id)

    def list_all(self) -> list[Subscription]:
        return self.db.query(Subscription).order_by(Subscription.id).all()

    def has_active_for_plan(self, customer_id: int, plan_id: int) -> bool:
        from app.models.enums import SubscriptionStatus

        existing = (
            self.db.query(Subscription)
            .filter(
                Subscription.customer_id == customer_id,
                Subscription.plan_id == plan_id,
                Subscription.status == SubscriptionStatus.ACTIVE.value,
            )
            .first()
        )
        return existing is not None

    def update(self, subscription: Subscription) -> Subscription:
        self.db.flush()
        return subscription


class InvoiceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, invoice: Invoice) -> Invoice:
        self.db.add(invoice)
        self.db.flush()
        return invoice

    def get_by_id(self, invoice_id: int) -> Invoice | None:
        return self.db.get(Invoice, invoice_id)

    def list_all(
        self,
        subscription_id: int | None = None,
        customer_id: int | None = None,
    ) -> list[Invoice]:
        query = self.db.query(Invoice)
        if subscription_id is not None:
            query = query.filter(Invoice.subscription_id == subscription_id)
        if customer_id is not None:
            query = query.filter(Invoice.customer_id == customer_id)
        return query.order_by(Invoice.id).all()

    def update(self, invoice: Invoice) -> Invoice:
        self.db.flush()
        return invoice


class PaymentAttemptRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payment: PaymentAttempt) -> PaymentAttempt:
        self.db.add(payment)
        self.db.flush()
        return payment

    def list_by_invoice(self, invoice_id: int) -> list[PaymentAttempt]:
        return (
            self.db.query(PaymentAttempt)
            .filter(PaymentAttempt.invoice_id == invoice_id)
            .order_by(PaymentAttempt.id)
            .all()
        )


class LedgerRepository:
    """Only create and read — no update or delete (append-only ledger)."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, entry: LedgerEntry) -> LedgerEntry:
        self.db.add(entry)
        self.db.flush()
        return entry

    def list_by_customer(self, customer_id: int) -> list[LedgerEntry]:
        return (
            self.db.query(LedgerEntry)
            .filter(LedgerEntry.customer_id == customer_id)
            .order_by(LedgerEntry.id)
            .all()
        )
