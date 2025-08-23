from django.urls import path
from .views import *

urlpatterns = [
    path('admin/', AdminUserListView.as_view(), name='admin-user-list'),
    path('gametables/', GetGameTableListView.as_view(), name='admin-game-table-list'),
]