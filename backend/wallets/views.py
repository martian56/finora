from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Wallet, Transaction, Deposit, Withdrawal
from .serializers import WalletSerializer, TransactionSerializer, DepositSerializer, WithdrawalSerializer


class WalletViewSet(viewsets.ModelViewSet):
    """ViewSet for Wallet model."""
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user).select_related('currency')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for Transaction model."""
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).select_related('wallet')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DepositViewSet(viewsets.ModelViewSet):
    """ViewSet for Deposit model."""
    queryset = Deposit.objects.all()
    serializer_class = DepositSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Deposit.objects.filter(user=self.request.user).select_related('currency')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WithdrawalViewSet(viewsets.ModelViewSet):
    """ViewSet for Withdrawal model."""
    queryset = Withdrawal.objects.all()
    serializer_class = WithdrawalSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Withdrawal.objects.filter(user=self.request.user).select_related('currency')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BalanceView(APIView):
    """Get user balances."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        wallets = Wallet.objects.filter(user=request.user)
        serializer = WalletSerializer(wallets, many=True)
        return Response(serializer.data)


class CreateDepositView(APIView):
    """Create a deposit."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = DepositSerializer(data=request.data)
        if serializer.is_valid():
            deposit = serializer.save(user=request.user)
            return Response(DepositSerializer(deposit).data, 
                          status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateWithdrawalView(APIView):
    """Create a withdrawal."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = WithdrawalSerializer(data=request.data)
        if serializer.is_valid():
            withdrawal = serializer.save(user=request.user)
            return Response(WithdrawalSerializer(withdrawal).data, 
                          status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransferView(APIView):
    """Transfer between wallets."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # This would implement wallet-to-wallet transfers
        return Response({'message': 'Transfer functionality not implemented yet'}, 
                      status=status.HTTP_501_NOT_IMPLEMENTED)