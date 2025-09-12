from django.urls import path
from .views import *

urlpatterns = [
    path('game/', GameTableView.as_view()),
    path('players/', PlayerView.as_view()),
    path('card-distribute/', DistributeCardsView.as_view()),
    path('bet/', BetView.as_view()),
    path('ranking/', HandRankingView.as_view()),
    path('spin-wheel/', SpinWheelAPIView.as_view(), name='spin-wheel'),
    path("game/start/", StartGameView.as_view(), name="start-game"),
    
    path("mastercards/", MasterCardMasterCard.as_view(), name="mastercards"),
    path('mastercards/<int:master_card_id>/', MasterCardMasterCard.as_view(), name='mastercard-detail'),

    path('bonus-wallet/balance/', BonusWalletBalanceAPIView.as_view(), name='bonus-wallet-balance'),


    

]