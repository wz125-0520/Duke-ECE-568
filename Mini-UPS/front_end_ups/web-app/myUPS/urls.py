"""myUPS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from ups import views as ups_views
from ups.views import (SearchCreateView,
                    SearchListView,
                    PackageListView,
                    PackageUpdateView,
                    PackageEvaUpdateView)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', ups_views.home, name='home'),
    path('admin/', admin.site.urls),
    path('register/', ups_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='ups/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='ups/logout.html'), name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='ups/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='ups/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='ups/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='ups/password_reset_complete.html'), name='password_reset_complete'),
    path('profile/', ups_views.profile, name='profile'),
    path('tracking/', ups_views.SearchCreateView.as_view(), name='search-create'),
    path('tracking/result/', ups_views.SearchListView.as_view(), name='search-list'),
    path('package/', ups_views.PackageListView.as_view(), name='package-list'),
    path('package/<int:pk>/update', ups_views.PackageUpdateView.as_view(), name='package-update'),
    path('package/<int:pk>/eva_update', ups_views.PackageEvaUpdateView.as_view(), name='package-evaupdate')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
