from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Count, Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import KBEntry, QueryLog
from .permissions import IsAdminUserRole
from .serializers import LoginSerializer, QuerySerializer, RegisterSerializer


def _access_token_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = User.objects.create_user(
            username=data["username"],
            password=data["password"],
            email=data["email"],
        )

        # Company profile is created by signal on User creation.
        company = user.company
        company.company_name = data["company_name"]
        company.save(update_fields=["company_name"])

        token = _access_token_for_user(user)
        return Response(
            {
                "username": user.username,
                "company_name": company.company_name,
                "api_key": company.api_key,
                "token": token,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = authenticate(username=data["username"], password=data["password"])
        if not user:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        company = user.company
        token = _access_token_for_user(user)
        return Response(
            {
                "token": token,
                "company_name": company.company_name,
                "api_key": company.api_key,
            },
            status=status.HTTP_200_OK,
        )


@api_view(["POST"])
def query_kb(request):
    serializer = QuerySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    search = serializer.validated_data["search"]

    company = request.user.company
    matches = KBEntry.objects.filter(
        Q(question__icontains=search) | Q(answer__icontains=search)
    )

    results = [
        {
            "id": row.id,
            "question": row.question,
            "answer": row.answer,
            "category": row.category,
        }
        for row in matches
    ]

    QueryLog.objects.create(
        company=company,
        search_term=search,
        result_count=len(results),
    )

    return Response(
        {
            "search": search,
            "count": len(results),
            "results": results,
        },
        status=status.HTTP_200_OK,
    )


class UsageSummaryView(APIView):
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        total_queries = QueryLog.objects.count()
        active_companies = QueryLog.objects.values("company_id").distinct().count()

        top_terms = (
            QueryLog.objects.values("search_term")
            .annotate(count=Count("id"))
            .order_by("-count")[:5]
        )

        return Response(
            {
                "total_queries": total_queries,
                "active_companies": active_companies,
                "top_search_terms": list(top_terms),
            },
            status=status.HTTP_200_OK,
        )
