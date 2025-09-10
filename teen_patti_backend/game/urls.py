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


    

]