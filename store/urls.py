from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_login, name='admin_login'),  # 👈 default page now = login
    path('about/', views.about, name='about'),
    path('products/', views.products, name='products'),
    path('products/category/<str:cat>/', views.products_by_category, name='products_by_category'),
    path('product/<int:pid>/', views.product_detail, name='product_detail'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('add_product/', views.add_product, name='add_product'),
    path('logout/', views.logout_view, name='logout'),
]