from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

# Register specific paths BEFORE the catch-all empty path
# Order matters - more specific routes must come first
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
router.register(r'deposits', views.DepositViewSet, basename='deposit')
router.register(r'withdrawals', views.WithdrawalViewSet, basename='withdrawal')

urlpatterns = [
    # Include router URLs for transactions, deposits, withdrawals
    path('', include(router.urls)),
    
    # Wallet viewset needs custom paths to avoid conflicts
    path('', views.WalletViewSet.as_view({'get': 'list', 'post': 'create'}), name='wallet-list'),
    path('<int:pk>/', views.WalletViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='wallet-detail'),
]
