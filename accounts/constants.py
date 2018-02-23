# URLS
OAUTH_LOGIN_URL = '/o/token/'
OAUTH_REVOKE_TOKEN_URL = '/o/revoke_token/'
EMAIL_VERIFICATION_URL = '/accounts/verify/email/'
FORGOT_PASSWORD_EMAIL_URL = '/accounts/reset/password/'


# Email Subjects
EMAIL_VERIFICATION_EMAIL_SUBJECT = 'Welcome to BearStateCoffee. Verify Your Email.'
FORGOT_PASSWORD_EMAIL_SUBJECT = 'Reset Your Password'


# Email Messages
EMAIL_VERIFICATION_EMAIL_DEFAULT_MESSAGE = 'Click on the following url to verify your email address.\n '
FORGOT_PASSWORD_EMAIL_DEFAULT_MESSAGE = 'Click on the following url to reset your password.\n '


# Important Messages To Be Sent With Response
SUCCESS_MESSAGE = 'Success.'
FAILURE_MESSAGE = 'Some problem occurred.'

SUCCESS_ON_SENDING_EMAIL = 'Email sent.'
INVALID_EMAIL = 'Invalid email.'

USER_EXISTS = 'User already exists.'
USER_INVALID = 'Invalid user or invalid credentials.'
USER_REGISTERED = 'User registered successfully.'
USER_TYPE_INVALID = 'Invalid user type.'
VERIFY_EMAIL = 'Verify your email first.'

OAUTH_TOKEN_REVOKED_SUCCESS = 'Token successfully revoked.'

VERIFY_EMAIL_HTTP_SUCCESS = '<h1>Email Address Successfully Verified</h1>'
RESET_PASSWORD_HTTP_SUCCESS = '<h1>You can verify your password</h1>'
HTTP_EXPIRED = '<h1>Link Expired</h1>'
HTTP_INVALID = '<h1>Link Doesn\'t Exists.</h1>'

LINK_EXPIRED = 'Link expired.'
LINK_INVALID = 'Link doesn\'t exists.'
PASSWORD_RESET_SUCCESS = 'Password reset successful.'


# Validation
RESET_PASSWORD_DATA_VALIDATION = 'Email not found.'
RESET_PASSWORD_VALIDATION = 'Password doesn\'t match.'
LOGIN_VALIDATION = 'Missing Email or Password.'
