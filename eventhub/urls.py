from django.urls import path

from .views import LoginView, RegisterView, UsageSummaryView, query_kb

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("kb/query/", query_kb, name="kb-query"),
    path("admin/usage-summary/", UsageSummaryView.as_view(), name="usage-summary"),
]
