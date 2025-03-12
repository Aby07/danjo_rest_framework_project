from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from .serializers import ProductSerializer
from .models import Product
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


#normal json based view
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
