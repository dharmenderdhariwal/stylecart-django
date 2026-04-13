from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from .forms import CheckoutForm
from .models import Category, Order, OrderItem, Product

def home(request):
    featured_products = Product.objects.filter(available=True, is_featured=True)[:8]
    latest_products = Product.objects.filter(available=True)[:8]
    categories = Category.objects.all()[:6]
    return render(request, 'shop/home.html', {
        'featured_products': featured_products,
        'latest_products': latest_products,
        'categories': categories,
    })

def product_list(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(available=True)
    if query:
        products = products.filter(Q(name__icontains=query) | Q(short_description__icontains=query))
    return render(request, 'shop/product_list.html', {'products': products, 'query': query})

def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.filter(available=True)
    return render(request, 'shop/category_products.html', {'category': category, 'products': products})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    return render(request, 'shop/product_detail.html', {'product': product})

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    cart = request.session.get('cart', {})
    key = str(product.id)
    cart[key] = cart.get(key, 0) + 1
    request.session['cart'] = cart
    messages.success(request, f'{product.name} added to cart.')
    return redirect(request.META.get('HTTP_REFERER', 'shop:product_list'))

def cart_detail(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        item_total = product.price * quantity
        total += item_total
        items.append({'product': product, 'quantity': quantity, 'item_total': item_total})
    return render(request, 'shop/cart.html', {'items': items, 'total': total})

def update_cart(request, product_id, action):
    cart = request.session.get('cart', {})
    key = str(product_id)
    if key in cart:
        if action == 'increase':
            cart[key] += 1
        elif action == 'decrease':
            cart[key] -= 1
            if cart[key] <= 0:
                del cart[key]
        elif action == 'remove':
            del cart[key]
    request.session['cart'] = cart
    return redirect('shop:cart')

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, 'Your cart is empty.')
        return redirect('shop:product_list')

    items = []
    total = 0
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        item_total = product.price * quantity
        total += item_total
        items.append({'product': product, 'quantity': quantity, 'item_total': item_total})

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(user=request.user, **form.cleaned_data)
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['product'].price,
                )
            request.session['cart'] = {}
            messages.success(request, 'Order placed successfully.')
            return redirect('shop:order_success', order_id=order.id)
    else:
        form = CheckoutForm(initial={
            'full_name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
        })

    return render(request, 'shop/checkout.html', {'form': form, 'items': items, 'total': total})

@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order_success.html', {'order': order})

@login_required
def my_orders(request):
    orders = request.user.orders.prefetch_related('items__product')
    return render(request, 'shop/my_orders.html', {'orders': orders})
