from django.urls import path
from . import views

app_name = 'trades'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('trades/', views.TradeListView.as_view(), name='trade_list'),
    path('trades/add/', views.TradeCreateView.as_view(), name='trade_create'),
    path('trades/<int:pk>/', views.TradeDetailView.as_view(), name='trade_detail'),
    path('trades/<int:pk>/edit/', views.TradeUpdateView.as_view(), name='trade_update'),
    path('trades/<int:pk>/delete/', views.TradeDeleteView.as_view(), name='trade_delete'),
    path('statistics/', views.StatisticsView.as_view(), name='statistics'),
]
