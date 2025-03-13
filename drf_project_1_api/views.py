from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from .serializers import ProductSerializer, OrderSerializer, OrderItemSerializer, ProductInfoSerializer
from .models import Product, Order, OrderItem
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

# normal json based view
# def product_list(request):
#     products = Product.objects.all()
#     print('products', products)
#     serializer = ProductSerializer(products, many=True)
#     return JsonResponse({
#         'data': serializer.data
#     }
#     )

# FUNCTION BASED VIEW 

@api_view(['GET', 'POST'])
def function_based_product_list_or_create(request):
    if request.method == 'GET':
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        data = request.data
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.error_messages)

@api_view(['GET', 'PUT', 'DELETE'])
def function_based_product_detail_update_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        data = request.data
        serializer = ProductSerializer(product, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)  
    
    elif request.method == 'DELETE':
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def function_based_order_list_for_nested_serializer(request):
    if request.method == 'GET':
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
@api_view(['GET'])
def product_info(request):
    products = Product.objects.all()
    serializer = ProductInfoSerializer({
        'products': products,
        'count': len(products),
        'max_price': products.aggregate(max_price=Max('price'))['max_price']
    })
    return Response(serializer.data)

# CLASS BASED VIEW - GENERIC VIEW

class GenericsBasedProductList(generics.ListAPIView): # list all product
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class GenericsBasedProductDetails(generics.RetrieveAPIView): #single product retrive
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'pk'

class GenericsBasedUserOrderList(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        return qs.filter(user=user)