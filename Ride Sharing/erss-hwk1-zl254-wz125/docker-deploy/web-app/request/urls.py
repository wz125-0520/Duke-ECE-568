from django.urls import path
from . import views
from .views import (
    PostListView,
    
    DriverCreateView,
    #DriverUpdateView,
    OwnerCreateView,
    SharerCreateView,
)
urlpatterns = [
    path('', views.home, name='request-home'),
    #path('driver/', views.driverInfo, name='request-driverInfo'),
	path('driver/new/', DriverCreateView.as_view(), name='driver-create'),
    #path('driver/<int:pk>/update/', DriverUpdateView.as_view(), name='driver-update'),
    path('driver/<int:RequestofOwner_id>/claim/',views.driverclaim, name='driver-claim'),
    path('driver/update/', views.driverupdate, name='driver-update'),
    path('driver/pick/', views.allorders, name='driver-pick'),
    path('test/', views.test, name='test'),
    path('owner/new/', OwnerCreateView.as_view(), name='owner-create'),
    #path('wait/', views.wait, name='owner-waiting'),
    path('sharer/new/', SharerCreateView.as_view(), name='sharer-create'),
    path('owner/orders/',views.orders, name='owner-orders'),
    #path('owner/ordersupdate',views.ordersupdate, name='owner-orders-update'),
    path('owner/<int:RequestofOwner_id>/detail',views.detail, name='owner-orders-update'),
    #view history
    path('driver/history/',views.driverhistory, name='driver-history'),
    path('driver/<int:RequestofOwner_id>/complete/',views.drivercomplete, name='driver-complete'),
    #view rides for sharer 
    path('sharer/join/view/',views.sharerjoinview, name='sharer-join-view'),
    path('sharer/<int:RequestofOwner_id>/join/',views.sharerjoin, name='sharer-join'),
    path('sharer/<int:RequestofOwner_id>/cancel/',views.sharercancel, name='sharer-cancel'),
    path('sharer/history',views.sharerhistory, name='sharer-history'),
]
