from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from .models import *


class ProductSerializer(serializers.ModelSerializer):
    price_with_tax = serializers.SerializerMethodField()
    collection_title = serializers.CharField(source='collection.title', read_only=True)

    def get_price_with_tax(self, obj):
        return obj.unit_price * Decimal(1.08)

    class Meta:
        model = Products
        fields = ('id', 'title', 'description', 'collection', 'collection_title', 'inventory', 'unit_price',
                  'price_with_tax')


class CollectionSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Collection
        fields = ('id', 'title', 'products_count')
        read_only_fields = ('id',)


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'date', 'description', 'name']

    def create(self, validated_data):
        product = Products.objects.get(pk=self.context.get('view').kwargs['product_pk'])
        return Review.objects.create(product_id=product.id, **validated_data)


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ['title', 'unit_price']


class CartItemSerializer(serializers.ModelSerializer):
    products = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, obj):
        return obj.products.unit_price * obj.quantity

    class Meta:
        model = CartItem
        fields = ('id', 'products', 'quantity', 'total_price')


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_cart_price = serializers.SerializerMethodField()

    def get_total_cart_price(self, obj):
        return sum([item.products.unit_price * item.quantity for item in obj.items.all()])

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_cart_price']


class AddCartItemSerializer(serializers.ModelSerializer):
    products_id = serializers.IntegerField()

    class Meta:
        model = CartItem
        fields = ['products_id', 'quantity']

    def save(self, **kwargs):
        cart_pk = self.context['view'].kwargs['cart_pk']
        try:
            cart = CartItem.objects.get(products_id=self.validated_data['products_id'])
            cart.quantity += self.validated_data['quantity']
            cart.save()
            self.instance = cart
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_pk, **self.validated_data)

        return self.instance


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()

    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'phone', 'birth_date', 'membership_choices']


class OrderItemSerializer(serializers.ModelSerializer):
    products = SimpleProductSerializer()

    class Meta:
        model = OrderItem
        fields = ('id', 'products', 'unit_price', 'quantity')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True, source='orderitems')

    class Meta:
        model = Order
        fields = ['id', 'customer', 'placed_at', 'payment_status', 'items']


class CreateOrderSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    cart_id = serializers.UUIDField(write_only=True)

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(id=cart_id).exists():
            raise serializers.ValidationError("Cart with this Id Doesn't Exist")
        return cart_id

    def validate(self, attrs):
        if CartItem.objects.filter(cart_id=attrs['cart_id']).count() == 0:
            raise serializers.ValidationError("Cart Is Empty")
        return attrs

    class Meta:
        model = Order
        fields = ['id', 'cart_id']

    def create(self, validated_data):
        with transaction.atomic():
            customer = Customer.objects.get(user_id=self.context.get('request').user.id)
            cart_items = CartItem.objects.select_related('products').filter(cart_id=validated_data['cart_id'])
            order = Order.objects.create(customer_id=customer.id)
            order_items = [OrderItem(order=order,
                                     products=item.products,
                                     quantity=item.quantity,
                                     unit_price=item.products.unit_price)
                           for item in cart_items]
            OrderItem.objects.bulk_create(order_items)

            return order


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']
