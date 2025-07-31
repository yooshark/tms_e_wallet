from django.urls import path
from wallets.views import (
    TransactionListCreateAPIView,
    TransactionRetrieveUpdateAPIView,
    WalletsBalanceAPIView,
    WalletsListCreateAPIView,
    WalletsRetrieveUpdateDestroyAPIView,
)

urlpatterns = [
    path("", WalletsListCreateAPIView.as_view(), name="list-create-wallets"),
    path(
        "<int:pk>/",
        WalletsRetrieveUpdateDestroyAPIView.as_view(),
        name="retrieve-update-destroy-wallet",
    ),
    path(
        "<int:pk>/balance/",
        WalletsBalanceAPIView.as_view(),
        name="retrieve-wallet-balance",
    ),
    path(
        "transactions/",
        TransactionListCreateAPIView.as_view(),
        name="list-create-transactions",
    ),
    path(
        "transactions/<int:pk>/",
        TransactionRetrieveUpdateAPIView.as_view(),
        name="retrieve-update-destroy-transaction",
    ),
]
