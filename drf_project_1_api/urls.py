
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.function_based_product_list_or_create),
    path('products/<int:pk>', views.function_based_product_detail_update_delete),
    path('products/info/', views.product_info),

    path('orders/', views.function_based_order_list_for_nested_serializer),
]
