from django.urls import path
from rest_framework_nested import routers
from . import views

router=routers.DefaultRouter()
router.register('products',views.ProductsViewSet,basename='product')
router.register('collections',views.CollectionsViewSet)
router.register('carts',views.CartViewset)
router.register('customers',views.CustomerViewSet)
router.register('orders',views.OrderViewSet,basename='orders')

products_router=routers.NestedDefaultRouter(router, 'products',lookup='product')
products_router.register('reviews', views.ReviewsViewSet,basename='product-reviews')

carts_router=routers.NestedDefaultRouter(router, 'carts',lookup='cart')
carts_router.register('items', views.CariItemViewSet,basename='cart-items')

urlpatterns=router.urls + products_router.urls + carts_router.urls

# urlpatterns=[
#     path('products/',views.Products.as_view()),
#     path('products/<int:pk>/',views.ProductDetail.as_view()),
#     path('collections/',views.Collections.as_view()),
#     path('collections/<int:pk>/',views.CollectionDetail.as_view())
# ]