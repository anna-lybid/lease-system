from django.urls import path, include
from rest_framework import routers
from .views import (
    GoalViewSet,
    ProductViewSet,
    ContractViewSet,
    UploadCSVView,
    ContractOnScreenView,
    ContractDownloadView
)

app_name = 'process'

router = routers.DefaultRouter()
router.register('goals', GoalViewSet, basename='goals')

urlpatterns = [
    path("", include(router.urls)),
    path('goals/<int:goal_pk>/products/', ProductViewSet.as_view({'get': 'list', 'post': 'create'}), name='product-list'),
    path('goals/<int:goal_pk>/products/<int:pk>/', ProductViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='product-detail'),
    path('goals/<int:goal_pk>/products/<int:product_pk>/contracts/', ContractViewSet.as_view({'get': 'list', 'post': 'create'}), name='contract-list'),
    path('goals/<int:goal_pk>/products/<int:product_pk>/contracts/<int:pk>/', ContractViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='contract-detail'),
    path('goals/<int:goal_pk>/products/<int:product_pk>/upload_csv/', UploadCSVView.as_view(), name='upload_csv'),
    path('goals/<int:goal_pk>/products/<int:pk>/contracts/<int:contract_id>/calculate_screen/', ContractOnScreenView.as_view(), name='contract_on_screen'),
    path('goals/<int:goal_pk>/products/<int:pk>/contracts/<int:contract_id>/calculate_download/', ContractDownloadView.as_view(), name='contract_on_screen'),
]
