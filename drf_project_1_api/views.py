from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import OrderFilter, ProductFilter
from .models import Order, OrderItem, Product
from .serializers import (OrderItemSerializer, OrderSerializer,
                          ProductInfoSerializer, ProductSerializer, OrderCreateSerializer)

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

class GenericsBasedProductCreate(generics.CreateAPIView): 
    model = Product
    serializer_class = ProductSerializer

class GenericsBasedProductCreateList(generics.ListCreateAPIView): 
    queryset = Product.objects.order_by('pk')
    serializer_class = ProductSerializer
    #filterset_fields = ['name'] #filtering based on the default attribute filterset
    filterset_class = ProductFilter # created a filter class on filter.py
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name']

    pagination_class = PageNumberPagination
    pagination_class.page_size = 4
    pagination_class.page_query_param = 'pgnm' # change query name
    pagination_class.page_size_query_param = 'page_size' # dynamically add page size in query parameter
    max_page_size = 7

    def get_permissions(self): # override the permission 
        self.permission_classes = [AllowAny]
        if self.request.method == 'POST':
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

class GenericsBasedProductDetails(generics.RetrieveAPIView): #single product retrive
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'pk'

class GenericsBasedProductRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_url_kwarg = 'pk'

    def get_permissions(self): # override the permission 
        self.permission_classes = [AllowAny]
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


class GenericsBasedUserOrderList(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        return qs.filter(user=user)

# CLASS BASED VIEW - API VIEW

class ApiViewBasedProductInfo(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductInfoSerializer({
            'products': products,
            'count': len(products),
            'max_price': products.aggregate(max_price=Max('price'))['max_price']
        })
        return Response(serializer.data)

# CLASS BASED VIEW - VIEWSETS

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        # can also check if POST: if self.request.method == 'POST'
        if self.action == 'create' or self.action == 'update':
            return OrderCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs