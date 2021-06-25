from django.contrib import admin
from .models import Product, Purchase
# Register your models here.
from django.contrib.auth.models import User, Group
admin.site.unregister(Group)

admin.site.register(Product)
admin.site.register(Purchase)


admin.site.site_header = "Analyzer Admin"
admin.site.site_title = "Analyzer Admin "
admin.site.index_title = " Analyzer Admin"