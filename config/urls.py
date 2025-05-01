"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from app.views import login_view,update_expense, delete_expense, expensses_list, deliver_contract, deliverable_contract, create_contract,update_user, delete_user, logout_user, user_list, home,delete_contract, contract_list,contract_details, contract_template, create_deliverable, update_contract, update_contract_image
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name='login'),
    path('logout-user', logout_user, name='logout'),
    
    path('home/', home, name='home'),
    path('contract-details/<int:pk>/', contract_details, name='contract_details'),
    path('contract-template/<int:pk>/', contract_template, name='contract_template'),
    path('update-contract-image/<int:pk>/', update_contract_image, name='update_contract_image'),
    
    path('create-deleiverable/<int:contract_id>/', create_deliverable, name='create_deliverable'),
    path('contract-update/<int:pk>/', update_contract, name='update_contract'),
    path('contract-delete/<int:pk>/', delete_contract, name='delete_contract'),
    
    path('contracts/', contract_list, name='contracts'),
    
    path('create-contract/', create_contract, name='create_contract'),
    path('users-list/', user_list, name='user_list'),
    path('user-update/<int:pk>/', update_user, name='user_list'),
    path('user-delete/<int:pk>/', delete_user, name='user_list'),
    path('deliver-contract/<int:pk>/', deliver_contract, name='deliver_contract'),
    
    path('deliverable-contract/', deliverable_contract, name='deliverable_contract'),
    path('expensses/', expensses_list, name='expensses'),
    path('update-expense/', update_expense, name='update_expense'),
    path('delete_expense/', delete_expense, name='delete_expense'),
    

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
