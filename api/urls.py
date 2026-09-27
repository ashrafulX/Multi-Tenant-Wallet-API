from django.urls import path,include
from rest_framework_nested import routers

from tenants.views import TenantViewSet
from wallets.views import WalletViewSet
from ledger.views import TransactionViewSet

router=routers.DefaultRouter()
router.register('tenants',TenantViewSet,basename='tenants')
router.register('wallets',WalletViewSet,basename='wallets')
router.register("transactions", TransactionViewSet, basename="transactions")

urlpatterns = [
    path('',include(router.urls)),
    path('auth/',include('djoser.urls')),
    path('auth/',include('djoser.urls.jwt')),
    # path("api/transfers/", TransferCreateView.as_view(), name="transfer-create"),
    


]