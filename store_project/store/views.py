import json
import datetime
from django.shortcuts import render
from .models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import cookieCart, cartData, guestOrder


def store(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'store/store.html', context=context)


def cart(request):
   data = cartData(request)

   cartItems = data['cartItems']
   order = data['order']
   items = data['items']

   context = {'items': items, 'order': order, 'cartItems': cartItems}
   return render(request, 'store/cart.html', context=context)


def checkout(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context=context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(product=product, order=order)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()
    return JsonResponse('Item was edded', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    print("data", data)
    
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    
    else:
        print("User is not logged in...")
        customer, order = guestOrder(request, data)
    
    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if str(total) == str(order.get_cart_total):
        
        order.complete = True

    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer = customer,
            order = order, 
            address = data['shipping']['address'],
            city = data['shipping']['city'],
            state = data['shipping']['state'],
            zipcode = data['shipping']['zipcode'],
        )
    print(request.body)
    return JsonResponse("Payment complete!", safe=False)