from os import name
from django.shortcuts import render, redirect
from .models import Adress, Cart, Order, OrderItem, Customer, Restaurant, Menu, Menu_Category
from django.http import HttpRequest, JsonResponse
from django.db import transaction
from django.db.utils import IntegrityError
from django.contrib import messages
from .forms import CustomerAdressForm, RegisterForm, LoginForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required


#****------BUNU YAPILANDIRACAĞIZ----------*****
# def addAdress(request):
#     form = CustomerAdressForm(request.POST or None)
#     customer = request.user
#     if request.method == "POST" and form.is_valid():
#         form.save()
#         messages.success(request, 'Your address has been created.')
#         return redirect('profile')
#     return render(request, 'addAdress.html', {'form': form})



def index(request):
      
    restaurants = Restaurant.objects.all()[:10]

    return render(request, 'index.html', {'restaurants': restaurants})

def Login(request):
    if request.user.is_authenticated:
        return redirect('index')

    form = LoginForm(request.POST or None)
    
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')

        customer = authenticate(request, email=email, password=password)
        if customer and not customer.is_superuser:
            login(request, user=customer)
            messages.success(request, 'You have successfully logged in.')
            return redirect('index')
        else:
            messages.error(request, 'Invalid email or password.')
            return redirect('login')

    return render(request, 'login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('index')

def register(request):
    if request.user.is_authenticated:
        return redirect('index')

    form = RegisterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, 'Your account has been created.')
        return redirect('login')

    return render(request, 'register.html', {'form': form})


def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def termsconditions(request):
    return render(request, 'termsconditions.html')

def privacy(request):
    return render(request, 'privacy.html')

def custom_404(request, exception):
    return render(request, '404.html', status=404)

@login_required(login_url='/login')
def profile(request):
    
    customer = request.user
    users = Customer.objects.filter(email=customer.email)
    customer_adress = Adress.objects.filter(customer=request.user)
    order_history = Order.objects.filter(customer=customer).prefetch_related('orderitems__menu').order_by('-created_at')
    context = {'users': users, 'customer_adress': customer_adress, 'order_history': order_history}
    return render(request, 'profile.html', context)

    
@login_required(login_url='/login')  # Requires the user to be authenticated
def detailRestaurant(request, name_slug):
    if request.method == "POST":
        # Sepetin dolu olup olmadığını kontrol et
        cart_items = Cart.objects.filter(customer=request.user)
        if not cart_items.exists():
            # Eğer sepet boşsa, kullanıcıya hata mesajı göster
            messages.error(request, 'Your cart is empty.')
            return redirect('detail-restaurant', name_slug=name_slug)
        else:
            # Sepet doluysa, kullanıcıyı 'order' sayfasına yönlendir
            return redirect('order')
    
    restaurant = Restaurant.objects.get(name_slug=name_slug)
    food_items = Menu.objects.filter(restaurant=restaurant)
    cart_items = Cart.objects.filter(customer=request.user)
    total_price = sum(item.total_price for item in cart_items)
    menu_categories = Menu_Category.objects.filter(menu_items__restaurant=restaurant).distinct()
    menu_slugs = [category.menu_slug for category in menu_categories]

    context = {
        'food_items': food_items,
        'restaurant': restaurant,
        'cart_items': cart_items,
        'total_price': total_price,
        'menu_categories': menu_categories,
        'menu_slugs': menu_slugs,
    }
    return render(request, 'detail-restaurant.html', context)



@login_required(login_url='/login')
def add_to_cart(request, menu_id):
    if request.method == "POST":
        try:
            menu = Menu.objects.get(id=menu_id)
            selected_quantity = int(request.POST.get('quantity', 1))
            name_slug = menu.restaurant.name_slug
            request.session['restaurant'] = name_slug

            if menu.quantity < selected_quantity:
                return JsonResponse({"success": False, "message": "Insufficient menu item quantity."})

            cart_item = Cart.objects.filter(customer=request.user, menu=menu).first()

            if cart_item:
                cart_item.quantity += selected_quantity
                cart_item.save()
            else:
                Cart.objects.create(
                    customer=request.user,
                    menu=menu,
                    quantity=selected_quantity
                )
            
            return JsonResponse({"success": True, "message": "Menu item added to cart"})
        
        except (Menu.DoesNotExist, ValueError):
            return JsonResponse({"success": False, "message": "Menu item not found or invalid data."})


@login_required(login_url='/login')  # Requires the user to be authenticated
def remove_from_cart(request, id):
    try:
        # Find the cart item by its ID, associated with the authenticated user (Customer)
        cart_item = Cart.objects.filter(customer=request.user, id=id).first()

        if cart_item:
            # Remove the cart item
            cart_item.delete()
            return JsonResponse({"success": True, "message": "Product removed from cart."})
        else:
            return JsonResponse({"success": False, "message": "Product not found in the cart."})

    except (Cart.DoesNotExist, ValueError):
        return JsonResponse({"success": False, "message": "Cart item not found or invalid data."})

# simdi order sayfasında restoranın name_slug'ını alıp, order sayfasına gönderiyoruz.
# sonra order sayfasında, name_slug'ı kullanarak restoranı buluyoruz.
# order sayfasında, sepetin dolu olup olmadığını kontrol ediyoruz.
# eğer sepet boşsa, kullanıcıya hata mesajı gösteriyoruz. ve restoranın sayfasına yönlendiriyoruz.

@login_required(login_url='/login')
def order(request):
    form = OrderForm(request.POST or None)
    customer = request.user
    cart_items = Cart.objects.filter(customer=request.user)
    total_price = sum(item.total_price for item in cart_items)
    addresses = Adress.objects.filter(customer=customer)
    context = {
        'addresses': addresses,
        'form': form,
        'cart_items': cart_items,
        'total_price': total_price,
    }

    if request.method == "POST" and form.is_valid():
        selected_address_id = request.POST.get('address')
        shipping_address = Adress.objects.filter(id=selected_address_id).first()

        if not shipping_address:
            messages.error(request, "Please select a valid address.")
            return redirect('restaurant-list')

        cart_items = Cart.objects.filter(customer=customer)
        if not cart_items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect('restaurant-list')

        for item in cart_items:
            if item.menu.quantity < item.quantity and item.menu.quantity != None:
                messages.error(request, f"{item.menu.name} doesn't have enough stock.")
                return render(request, 'order.html', context)

        with transaction.atomic():
            order = Order.objects.create(
                customer=customer,
                shipping_address=shipping_address,
                total_price=sum(item.total_price for item in cart_items),
                status='pending'
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    menu=item.menu,
                    quantity=item.quantity,
                )
                item.menu.quantity -= item.quantity
                item.menu.save()

            cart_items.delete()
            messages.success(request, 'Your order has been placed successfully.')
            return redirect('confirm')
    
    cart_items = Cart.objects.filter(customer=customer)
    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('restaurant-list')

    return render(request, 'order.html', context)



def confirmorder(request):
    return render(request, 'confirm.html')
