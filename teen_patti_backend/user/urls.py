from django.urls import path,re_path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
      path('register/', RegisterView.as_view()),
      path('verify/', Verify.as_view()),
      path('me/', RetrieveUserView.as_view()),
      path('revoke-access-token/', RevokeAccessTokenView.as_view(), name='revoke-access-token'),
      path('verification-resend-email/', EmailResendView.as_view(), name='resend-email'),
      path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
      path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
      path('user/reset_email/', ResetEmailView.as_view(), name='reset_email'),
      path('email-verify/', ResettingEmailVerify.as_view()),
      path('forgot-password/', ForgotPasswordAPIView.as_view(), name='forgot-password'),
      path('reset-password/', ResetPasswordAPIView.as_view(), name='reset-password'),
      path('wallet-balance/', WalletBalanceView.as_view(), name='wallet-balance'),
      path('referral-balance/', ReferralLinkView.as_view(), name='referral-balance'),
      path('recharge-api/', RechargeAPIView.as_view(), name='referral-balance'),
      re_path(r'^o/(?P<provider>\S+)/$',CustomProviderAuthView.as_view(),name='provider-auth'),
]