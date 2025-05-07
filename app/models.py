from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('Phone number is required')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(max_length=15, unique=True)
    name = models.CharField(default='', max_length=200) 
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.phone


class Contract(models.Model):
    client_name = models.CharField(max_length=220)
    client_id = models.CharField(max_length=14)
    client_address = models.CharField(max_length=220)
    contract_date = models.DateField()
    recieve_date = models.DateField()
    contract_total = models.DecimalField(max_digits=10, decimal_places=2)
    remain= models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    employee_name = models.CharField(max_length=200, default=' ')
    contract_header_image = models.ImageField(upload_to='contracts', default='logo.jpg')
    is_deliver = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.remain = self.contract_total
        return super().save(*args, **kwargs)
    
    class Meta:
        ordering = ('-contract_date', )


class Product(models.Model):
    Contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='products')
    product_title = models.CharField(max_length=600)
    total_price = models.DecimalField(max_digits=9, decimal_places=2)
    notes = models.TextField(default=' ')
    product_image = models.ImageField(null=True, blank=True, upload_to='products')


class Deliverable(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='deliverables')
    delivery_date = models.DateField()
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    note = models.TextField(default=' ')
    employee_name = models.CharField(max_length=200, default='----')


class Expensses(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at =  models.DateTimeField(auto_now=True)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    direct_to = models.CharField(max_length=220)

    class Meta:
        ordering = ('created_at',)