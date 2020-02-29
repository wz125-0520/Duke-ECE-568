from django.contrib import admin
from .models import RequestofDriver,RequestofOwner,RequestofSharer

admin.site.register(RequestofDriver)
admin.site.register(RequestofOwner)
admin.site.register(RequestofSharer)