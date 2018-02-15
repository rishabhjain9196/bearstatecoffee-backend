from django.urls import path, re_path
from accounts.views import SignUpView, VerifyEmailView, ResetPasswordView, LoginView, LogoutView

urlpatterns = [
    path('signup/', SignUpView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    re_path('verify/email/(?P<token>.*)/', VerifyEmailView.as_view()),
    re_path('reset/password/(?P<token>.*)/', ResetPasswordView.as_view()),
]