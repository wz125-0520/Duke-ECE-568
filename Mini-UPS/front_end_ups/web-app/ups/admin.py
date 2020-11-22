from django.contrib import admin
from .models import Profile, Package, Search, Truck

admin.site.register(Profile)
admin.site.register(Package)
admin.site.register(Search)
admin.site.register(Truck)