from .models import Order, OrderItem
import json

def total_cart_items(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

        if order:
            cartItems = order.get_cart_quantity_items

        else:
            cartItems = 0
    
    else:
        try:
            cart = json.loads(request.COOKIES['cart'])
        except:
            cart = {}

        cartItems = 0
        for cart_item_index in cart:
            cartItems += cart[cart_item_index]['quantity']

        

    
    return {'cartItems': cartItems}