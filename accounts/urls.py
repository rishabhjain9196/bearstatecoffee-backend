from django.urls import path, re_path

from accounts.views import SignUpView, VerifyEmailView, ResetPasswordMailView, LoginView, LogoutView, \
    UserDetailsView, ResetPasswordSendMailView, ChangePasswordView

urlpatterns = [
    path('signup/', SignUpView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('profile/', UserDetailsView.as_view()),
    re_path('verify/email/(?P<token>.*)/', VerifyEmailView.as_view()),
    re_path('reset/password/(?P<token>.*)/', ResetPasswordMailView.as_view()),
    path('reset/password/send/mail/', ResetPasswordSendMailView.as_view()),
    path('change/password/', ChangePasswordView.as_view()),
]
