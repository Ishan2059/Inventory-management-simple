from django.urls import path
from . import views
from .views import notifications_view, mark_notification_as_read

urlpatterns = [
    path('', views.index, name='dashboard-index'),
    path('staff/', views.staff, name='dashboard-staff'),
    path('staff/detail/<int:pk>/', views.staff_detail, name='dashboard-staff-detail'),
    path('product/', views.product, name='dashboard-product'),
    path('product/delete/<int:pk>', views.product_delete, name='dashboard-product-delete'),
    path('product/update/<int:pk>', views.product_update, name='dashboard-product-update'),
    path('order/', views.order, name='dashboard-order'),
    path('notifications/', notifications_view, name='dashboard-notifications'),
    path('notifications/read/<int:notification_id>/', mark_notification_as_read, name='mark_notification_as_read'),
    path('predict-demand/<int:pk>/', views.predict_demand, name='predict-demand'),
]