
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .forms import ContractForm, ProductFormSet
from .models import Product, Contract, Deliverable, Expensses
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


@login_required
def home(request):
    return render(request, 'home.html')
from itertools import zip_longest
import decimal
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

@login_required
def create_contract(request):
    if request.method == 'POST':
        contract = Contract.objects.create(
            client_name=request.POST['client_name'],
            client_id=request.POST['client_id'],
            client_address=request.POST['client_address'],
            contract_date=request.POST['contract_date'],
            recieve_date=request.POST['recieve_date'],
            contract_total=0,
        )

        titles = request.POST.getlist('product_title[]')
        totals = request.POST.getlist('total_price[]')
        notes = request.POST.getlist('notes[]')
        images = request.FILES.getlist('image[]')

        total_amount = 0

        for title, total, note, image in zip_longest(titles, totals, notes, images):
            if not title or not total:
                continue  # Skip rows with missing essential info

            Product.objects.create(
                Contract=contract,
                product_title=title,
                total_price=decimal.Decimal(total),
                notes=note or "",
                product_image=image  # this will be None if not uploaded, which is fine
            )
            total_amount += decimal.Decimal(total)

        contract.contract_total = total_amount
        contract.remain = total_amount
        contract.save()

        return redirect(reverse('contract_details', kwargs={'pk': contract.id}))

    return render(request, 'create_contract.html')


@login_required
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


@login_required
def contract_details(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    return render(request, 'contract_details.html', {
        "contract": contract
    })


@login_required
def contract_template(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    return render(request, 'contract_template.html', {
        'contract': contract
    })


@login_required
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


@login_required
def update_contract(request, pk):
    contract = get_object_or_404(Contract, id=pk)

    if request.method == "POST":
        contract.client_name = request.POST['client_name']
        contract.client_id = request.POST['client_id']
        contract.client_address = request.POST['client_address']
        contract.contract_date = request.POST['contract_date']
        contract.recieve_date = request.POST['recieve_date']

        titles = request.POST.getlist('product_title[]')
        totals = request.POST.getlist('total_price[]')
        notes = request.POST.getlist('notes[]')
        product_ids = request.POST.getlist('product_id[]')
        images = request.FILES.getlist('image[]')

        total_amount = decimal.Decimal('0.0')

        # Track IDs submitted in form
        submitted_ids = set()
        image_index = 0

        for i in range(len(titles)):
            title = titles[i]
            price = totals[i]
            note = notes[i] if i < len(notes) else ''
            prod_id = product_ids[i] if i < len(product_ids) else ''

            image = None
            if image_index < len(images):
                image = images[image_index]
                image_index += 1

            if prod_id:
                submitted_ids.add(int(prod_id))
                product = Product.objects.filter(id=prod_id, Contract=contract).first()
                if product:
                    product.product_title = title
                    product.total_price = decimal.Decimal(price)
                    product.notes = note
                    if image:
                        product.product_image = image
                    product.save()
            else:
                new_product = Product.objects.create(
                    Contract=contract,
                    product_title=title,
                    total_price=decimal.Decimal(price),
                    notes=note,
                    product_image=image if image else None
                )
                submitted_ids.add(new_product.id)

            total_amount += decimal.Decimal(price)

        # Delete removed products
        existing_ids = set(contract.products.values_list('id', flat=True))
        ids_to_delete = existing_ids - submitted_ids
        Product.objects.filter(id__in=ids_to_delete).delete()

        contract.contract_total = total_amount
        contract.remain = total_amount
        contract.save()

        return redirect(reverse('contract_details', kwargs={'pk': contract.id}))

    return render(request, 'update_contract.html', {'contract': contract})

@login_required
def delete_contract(reqeust, pk):
    contract = get_object_or_404(Contract, pk=pk)
    contract.delete()
    return redirect('contracts')



@login_required
def update_contract_image(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    contract.contract_header_image = request.FILES["image"]
    contract.save()
    return redirect(reverse('contract_template', kwargs={'pk': pk}))


from .models import CustomUser

@login_required
def user_list(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        if name and phone and password:
            CustomUser.objects.create(name=name, phone=phone, password=password, is_staff=True)
            return redirect('user_list')

    query = request.GET.get('q')
    if query:
        users = CustomUser.objects.filter(name__icontains=query) | CustomUser.objects.filter(phone__icontains=query)
    else:
        users = CustomUser.objects.all()
    
    return render(request, 'users.html', {'users': users})

@login_required
def logout_user(request):
    logout(request)
    return redirect('login')


@login_required
def update_user(request, pk):
    try:
        user = get_object_or_404(CustomUser, pk=pk)
        user.name= request.POST.get("name", "")
        user.phone= request.POST.get("phone", "")
        user.save()
        return redirect('user_list')
    except:
        return HttpResponse("Something Went Wrong")

@login_required
def delete_user(request, pk):
    try:
        user = get_object_or_404(CustomUser, pk=pk)
        user.delete()
        return redirect("user_list")
    except:
        return HttpResponse("Something Went Wrong")
    
from django.db.models import Sum


@login_required
def deliverable_contract(request):
    query = request.GET
    month = query.get("month")
    start_date = query.get("start_date")
    end_date = query.get("end_date")

    contracts = Contract.objects.filter(is_deliver=True)
    expensess = Expensses.objects.all()

    if month:
        contracts = contracts.filter(contract_date__month=month)
        expensess = expensess.filter(created_at__month=month)
        contract_total = contracts.aggregate(total=Sum('contract_total'))["total"] or 0
        expensess_total = expensess.aggregate(total=Sum('amount'))["total"] or 0

        return render(request, 'deliverable_contract.html', {
        "contracts": contracts,
        "contract_total": contract_total,
        "expensess_total": expensess_total,
    })

    if start_date:
        contracts = contracts.filter(contract_date__gte=start_date)
        expensess = expensess.filter(created_at__gte=start_date)

    if end_date:
        contracts = contracts.filter(contract_date__lte=end_date)
        expensess = expensess.filter(created_at__lte=end_date)

    contract_total = contracts.aggregate(total=Sum('contract_total'))["total"] or 0
    expensess_total = expensess.aggregate(total=Sum('amount'))["total"] or 0

    return render(request, 'deliverable_contract.html', {
        "contracts": contracts,
        "contract_total": contract_total,
        "expensess_total": expensess_total,
    })



@login_required
def expensses_list(request):
    if request.method == "POST":
        Expensses.objects.create(
            description=request.POST.get("description", " "),
            amount=request.POST.get("amount"),
            direct_to=request.POST.get("source", " ")
        )
        return redirect('expensses')

    expensses = Expensses.objects.all()
    query = request.GET

    month = query.get("month")
    start_date = query.get("start_date")
    end_date = query.get("end_date")

    if month:
        expensses = expensses.filter(created_at__month=month)
    if start_date:
        expensses = expensses.filter(created_at__date__gte=start_date)
    if end_date:
        expensses = expensses.filter(created_at__date__lte=end_date)

    total = expensses.aggregate(total_amount=Sum("amount"))["total_amount"] or 0

    return render(request, 'expensses.html', {
        "expensses": expensses,
        "total": total
    })


@login_required
def deliver_contract(request, pk):
    contract = Contract.objects.get(pk=pk)
    contract.is_deliver = True
    contract.save()
    return redirect(reverse('contract_details', kwargs={"pk":pk}))


@login_required
def update_expense(request):
    if request.method == 'POST':
        expense = get_object_or_404(Expensses, id=request.POST['id'])
        expense.description = request.POST['description']
        expense.amount = request.POST['amount']
        expense.direct_to = request.POST['source']
        expense.save()
    return redirect('expensses')  


@login_required
def delete_expense(request):
    if request.method == 'POST':
        expense = get_object_or_404(Expensses, id=request.POST['id'])
        expense.delete()
    return redirect('expensses')