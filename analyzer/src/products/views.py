from django.shortcuts import render
from .models import Product, Purchase
import pandas as pd
from .utils import get_simple_plot, get_salesman_from_id, get_image
from .forms import PurchaseForm
from django.http import HttpResponse
import matplotlib.pyplot as plt 
import seaborn as sns 
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from datetime import date, timedelta
# Create your views here.

from collections import defaultdict

@login_required
def sales_dist_view(request):
    df = pd.DataFrame(Purchase.objects.all().values())
    df['salesman_id'] = df['salesman_id'].apply(get_salesman_from_id)
    df.rename({'salesman_id':'salesman'}, axis=1, inplace=True)
    df['date'] = df['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
    # print(df)
    plt.switch_backend('Agg')
    plt.xticks(rotation=45,  fontsize = "7")
    plt.yticks(fontsize = "7")
    plt.tick_params(labelsize=8, width=0.5)
    plt.xlabel("Date")
    plt.ylabel("Total Sales")
    barplot = sns.barplot(x='date', y='total_price', hue='salesman', data=df)
    # plt.setp(barplot.get_legend().get_texts(), fontsize='5')  
  
# for legend title
    barplot.legend(fontsize  = 8)
    # plt.setp(barplot.get_legend().get_title(), fontsize='10')  
    plt.tight_layout()
    graph = get_image()
    print("current user : ", request.user.id, request.user.username)
    print("all userS: ")
    for i in User.objects.all():
        print( i.id, i.username)

    # return HttpResponse("hello salesman")
    return render(request, 'products/sales.html', {'graph': graph})

@login_required
def chart_select_view(request):
    graph = None
    error_message=None
    df = None
    price = None 

    try:
        product_df = pd.DataFrame(Product.objects.all().values())
        purchase_df = pd.DataFrame(Purchase.objects.all().values())
        product_df['product_id'] = product_df['id']
    
        if purchase_df.shape[0] > 0:
            df = pd.merge(purchase_df, product_df, on='product_id').drop(['id_y', 'date_y'], axis=1).rename({'id_x': 'id', 'date_x': 'date'}, axis=1)
            price = df['price']
            if request.method == 'POST':
                chart_type = request.POST.get('sales')
                date_from = request.POST['date_from']
                date_to = request.POST['date_to']
                print(chart_type)
                df['date'] = df['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
                df2 = df.groupby('date', as_index=False)['total_price'].agg('sum')

                if chart_type != "":
                    if date_from != "" and date_to != "":
                        df = df[(df['date']>date_from) & (df['date']< date_to)]
                        df2 = df.groupby('date', as_index=False)['total_price'].agg('sum')
                    graph = get_simple_plot(chart_type, x=df2['date'], y=df2['total_price'], data=df)
                else:
                    error_message = 'Please select a chart type to continue'

        else:
            error_message = 'No records in the database'
    except:
        product_df = None
        purchase_df = None
        error_message = 'No records in the database'
        
    context = {
        'graph' : graph,
        'price': price,
        'error_message': error_message,
    }
    return render(request, 'products/main.html', context)

@login_required
def add_purchase_view(request):
    form = PurchaseForm(request.POST or None)
    added_message=None

    if form.is_valid():
        obj = form.save(commit=False)
        obj.salesman = request.user
        obj.save()

        form = PurchaseForm()
        added_message = "The purchase has been added"

    context = {
        'form': form,
        'added_message': added_message,
    }
    return render(request, 'products/add.html', context)

    
@login_required
def generate_report(request):

    if request.method == "POST":

        duration = request.POST.get("duration")
        end = date.today() + timedelta(days  = 1)
        start = date.today()
        # if duration == "weeky":
        #     start = end  - timedelta(days = 7)

        # elif duration == "monthly":
        #     start = end  - timedelta(days = 30)

        # elif duration == "yearly":
        #     start = end  - timedelta(days = 365)

        if duration:
            try:

                duration = int(duration)
                start  = end  - timedelta(days = duration)
            except:
                pass

        purchase = Purchase.objects.filter(date__range = [start, end]).reverse()
        purchase = purchase[::-1]
        salesman_data =  dict()

        for x in purchase:
            try:
                if salesman_data[x.salesman.first_name + " " + x.salesman.last_name]:

                    salesman_data[x.salesman.first_name + " " + x.salesman.last_name]  += x.total_price

            except:
                salesman_data[x.salesman.first_name + " " + x.salesman.last_name]  = 0
                salesman_data[x.salesman.first_name + " " + x.salesman.last_name] += x.total_price



        print(salesman_data)

        return render(request, "products/report.html", {"start": start, "end" : end, "purchase" : purchase, "salesman_data" : salesman_data})

    else:
        return render(request, "products/report.html",{})

