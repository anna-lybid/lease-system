from django.urls import path, include
from rest_framework import routers
from .views import (
    GoalViewSet,
    ProductViewSet,
    ContractViewSet,
    UploadCSVView
)

app_name = 'process'

router = routers.DefaultRouter()
router.register('goals', GoalViewSet, basename='goals')
router.register('products', ProductViewSet, basename='products')
router.register('contracts', ContractViewSet, basename='contracts')

urlpatterns = [
    path("", include(router.urls)),
    path('upload_csv/<int:product_id>/', UploadCSVView.as_view(), name='upload_csv'),
]