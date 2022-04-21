from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import (CreateModelMixin, RetrieveModelMixin, DestroyModelMixin)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from .filters import ProductFilter
from .pagination import DefaultPagination
from .permissions import IsAdminOrReadOnly
from .serializers import *


class ProductViewSet(ModelViewSet):
    queryset = Products.objects.select_related('collection').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ['collection__title']

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(products_id=kwargs['pk']).count() > 0:
            return Response({'errors': 'Product with this id cannot be deleted because it is associated with an order \
                                        item'})
        return super().destroy(request, *args, **kwargs)


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count=Count('products')).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        if Products.objects.filter(collection_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Collection with this id cannot be deleted as its has '
                                      'products associated with it'})
        return super().destroy(request, *args, **kwargs)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])


class CartViewSet(CreateModelMixin,
                  RetrieveModelMixin,
                  DestroyModelMixin,
                  GenericViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):
    http_method_names = ['post', 'get', 'patch', 'delete']

    def get_queryset(self):
        return CartItem.objects.select_related('products').filter(cart_id=self.kwargs['cart_pk'])

    def get_serializer_class(self):
        if self.action in ['create']:
            return AddCartItemSerializer
        if self.action in ['partial_update']:
            return UpdateCartItemSerializer
        return CartItemSerializer


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminOrReadOnly]

    @action(detail=True, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        customer, created = Customer.objects.get_or_create(user_id=self.request.user.id)
        if request.method == "PUT":
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
