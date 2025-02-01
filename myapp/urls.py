from django.urls import path
from . import views
# urlpatterns=[
#     path("", views.home,name="home")
# ]

urlpatterns = [
    path('search/', views.product_search, name='product_search'),
    path("", views.home,name="home"),
    path('stores/', views.stores_view, name='stores'),
    path('categories/', views.categories_view, name='categories'),
    path('products/', views.products_view, name='products'),
    path('product/<str:product_id>/', views.product_details, name='product_details'),
    
]