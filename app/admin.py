from django.contrib import admin
from .models import Contract, Product, Deliverable, CustomUser
# Register your models here.

admin.site.register([CustomUser, Contract, Product, Deliverable])
