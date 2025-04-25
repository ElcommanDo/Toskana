
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from .forms import ContractForm, ProductFormSet
from .models import Product, Contract, Deliverable
from django.core.paginator import Paginator
from django.urls import reverse
import datetime, decimal

User = get_user_model()

def login_view(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        user = authenticate(request, phone=phone, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # or your dashboard
        else:
            return render(request, 'login.html', {'error': 'Invalid phone or password'})
    return render(request, 'login.html')




def home(request):
    return render(request, 'home.html')

def create_contract(request):
    if request.method == 'POST':
        contract = Contract.objects.create(
            client_name=request.POST['client_name'],
            client_id=request.POST['client_id'],
            client_address=request.POST['client_address'],
            contract_date=request.POST['contract_date'],
            recieve_date=request.POST['recieve_date'],
            contract_total=0,  # calculate if needed
            
        )

        titles = request.POST.getlist('product_title[]')
        totals = request.POST.getlist('total_price[]')
        notes = request.POST.getlist('notes[]')
        total_amount = 0
        for title, total, note in zip(titles, totals, notes):
            Product.objects.create(
                Contract=contract,
                product_title=title,
                total_price=decimal.Decimal(total),
                notes=note,
                product_image = request.FILES.get('image')
            )
        total_amount+=decimal.Decimal(total)
        contract.contract_total = total_amount
        contract.remain = total_amount
        
        contract.save()
        return redirect(reverse('contract_details', kwargs={'pk': contract.id}))
    
    return render(request, 'create_contract.html')


def contract_list(request):
    contracts = Contract.objects.all()

    # Filters
    client_name = request.GET.get("client_name")
    contract_date = request.GET.get("contract_date")
    recieve_date = request.GET.get("recieve_date")

    if client_name:
        contracts = contracts.filter(client_name__icontains=client_name)
    if contract_date:
        contracts = contracts.filter(contract_date=contract_date)
    if recieve_date:
        contracts = contracts.filter(recieve_date=recieve_date)

    # Pagination
    paginator = Paginator(contracts, 10)  
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'contracts.html', {
        'page_obj': page_obj,
        'contracts': page_obj.object_list,
    })


def contract_details(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    return render(request, 'contract_details.html', {
        "contract": contract
    })


def contract_template(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    return render(request, 'contract_template.html', {
        'contract': contract
    })


def create_deliverable(request, contract_id):
    try:
        data = request.POST
        contract = get_object_or_404(Contract, id=contract_id)
        obj = Deliverable()
        obj.contract = contract
        obj.delivery_date =  datetime.datetime.now().date()
        obj.amount = data['amount']
        obj.note = data.get('note', '')
        obj.employee_name = data.get('employee', '')
        obj.save()
        contract.remain -= decimal.Decimal(obj.amount)
        contract.save()
    except Exception as e:
        return HttpResponse(str(e))
    return redirect(reverse('contract_details', kwargs={'pk': contract_id}))



def update_contract(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    return render(request, 'update_contract.html', {
        'contract': contract
    })


def delete_contract(reqeust, pk):
    contract = get_object_or_404(Contract, pk=pk)
    contract.delete()
    return redirect('contracts')



def update_contract_image(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    contract.contract_header_image = request.FILES["image"]
    contract.save()
    return redirect(reverse('contract_template', kwargs={'pk': pk}))
