from rest_framework_nested import routers

from . import views

router = routers.DefaultRouter()
router.register('products', views.ProductViewSet)
router.register('collections', views.CollectionViewSet)
router.register('cart', views.CartViewSet)
router.register('customers', views.CustomerViewSet)
router.register('order', views.OrderViewSet, basename='order')

review_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
review_router.register('review', views.ReviewViewSet, basename='product-reviews')

cartitem_router = routers.NestedDefaultRouter(router, 'cart', lookup='cart')
cartitem_router.register('items', views.CartItemViewSet, basename='cart-cartitems')

urlpatterns = router.urls + review_router.urls + cartitem_router.urls
