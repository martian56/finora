from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.WalletViewSet, basename='wallet')
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
router.register(r'deposits', views.DepositViewSet, basename='deposit')
router.register(r'withdrawals', views.WithdrawalViewSet, basename='withdrawal')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
]
