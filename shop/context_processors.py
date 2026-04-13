from .models import Category

def cart_item_count(request):
    cart = request.session.get('cart', {})
    return {'cart_item_count': sum(cart.values())}

def categories_menu(request):
    return {'menu_categories': Category.objects.all()[:8]}
