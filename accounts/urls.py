from django.urls import path, re_path
from accounts.views import SignUpView, VerifyEmailView, ResetPasswordView

urlpatterns = [
    path('signup/', SignUpView.as_view()),
    re_path('verify/email/(?P<token>.*)/', VerifyEmailView.as_view()),
    re_path('reset/password/(?P<token>.*)/', ResetPasswordView.as_view()),
]