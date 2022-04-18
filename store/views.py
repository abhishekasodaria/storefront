from django.shortcuts import render
from django.db.models import F, Max, Count, Sum
from .models import *

def say_hello(request):

    customers = OrderItem.objects.annotate(total_sales=Sum(F('quantity') * F('unit_price'))).\
        values('products__title').order_by('-total_sales')[:5]

    return render(request, "hello.html", {"customers":customers})