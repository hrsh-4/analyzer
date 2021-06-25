from django.shortcuts import render
from .forms import CsvForm
from .models import Csv
import csv
from django.contrib.auth.models import User
from products.models import Product, Purchase
from django.contrib.auth.decorators import login_required
import datetime
# Create your views here.


print("in csv views")
@login_required
def upload_file_view(request):
    error_message = None
    success_message = None
    form = CsvForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        print("in if ")
        form.save()
        form = CsvForm()
     
        print(" in try")
        obj = Csv.objects.filter(activated=False).first()
        print("object creation")
        with open(obj.file_name.path, 'r') as f:
            reader = csv.reader(f)

            for row in reader:
                print("looping csv")
                print(row)
                row = "".join(row)
                print(row)
                row = row.replace(";", " ")
                row = row.split()
                print(row)
                user = User.objects.get_or_create(id = row[3])
                print("getting user")
                prod, _ = Product.objects.get_or_create(name=row[0])
                print("getting product ", prod)
                print("creating purchase")
                new_date = row[4] + " "+ row[5]
                # date = datetime.datetime.strptime(new_date, '%Y-%m-%d %H:%M:%S')
                # pint(date)
                print(prod,  row[2], row[1], (user[0]), new_date)
                Purchase.objects.create(
                    product=prod,
                    price = int(row[2]),
                    quantity = int(row[1]),
                    salesman = user[0],
                    date = new_date

                )
                print("last of iteration")

        obj.activated=True
        obj.save()
        success_message= "Uploaded sucessfully"
        error_message = "Ups. Something went wrong...."

    context = {
        'form': form,
        'success_message': success_message,
        'error_message': error_message,
    }
    return render(request, 'csvs/upload.html', context)