from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect

from .forms import SignUpForm, CheckoutForm
from .models import Product, ProductVariant, OrderItem, Order, Category


User = get_user_model()


def home(request):
    categories = Category.objects.all()
    products = Product.objects.filter(active=True).order_by("-created_at")

    q = request.GET.get("q", "").strip()
    if q:
        products = products.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q)
        )

    context = {
        "products": products,
        "categories": categories,
        "current_category": None,
        "current_search": q,
    }
    return render(request, "siteapp/home.html", context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, active=True)
    variants = product.variants.all()
    context = {
        "product": product,
        "variants": variants,
    }
    return render(request, "siteapp/product_detail.html", context)


def add_to_cart(request):
    if request.method != "POST":
        return redirect("home")

    # 🚫 Require login
    if not request.user.is_authenticated:
        messages.error(request, "Please log in to add items to your cart.")
        return redirect("login")

    variant_id = request.POST.get("variant_id")
    variant = get_object_or_404(ProductVariant, id=variant_id)

    # OUT OF STOCK
    if variant.stock <= 0:
        messages.error(request, "This item is out of stock.")
        return redirect("product_detail", slug=variant.product.slug)

    cart = request.session.get("cart", {})
    variant_id = str(variant_id)
    current_qty = cart.get(variant_id, 0)

    if current_qty + 1 > variant.stock:
        messages.error(request, f"Only {variant.stock} piece(s) available.")
        return redirect("cart")

    cart[variant_id] = current_qty + 1
    request.session["cart"] = cart

    messages.success(request, "Item added to cart.")
    return redirect("cart")


@login_required
def cart_page(request):
    cart = request.session.get("cart", {})

    items = []
    total = Decimal("0.00")

    for variant_id, qty in cart.items():
        variant = get_object_or_404(ProductVariant, id=variant_id)
        subtotal = variant.price * qty
        items.append({
            "variant": variant,
            "quantity": qty,
            "subtotal": subtotal,
        })
        total += subtotal

    context = {
        "items": items,
        "total": total,
    }
    return render(request, "siteapp/cart.html", context)


@login_required
def checkout(request):
    cart = request.session.get("cart", {})

    if not cart:
        return redirect("cart")

    # build items + total from cart
    items = []
    total = Decimal("0.00")
    for variant_id, qty in cart.items():
        variant = get_object_or_404(ProductVariant, id=variant_id)
        subtotal = variant.price * qty

        items.append({
            "variant": variant,
            "quantity": qty,
            "subtotal": subtotal,
        })
        total += subtotal

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if not form.is_valid():
            # form has errors, redisplay with items + total
            context = {
                "items": items,
                "total": total,
                "form": form,
            }
            return render(request, "siteapp/checkout.html", context)

        # valid data
        cleaned = form.cleaned_data
        name = cleaned["name"]
        phone = cleaned["phone"]
        address1 = cleaned["address_line1"]
        address2 = cleaned["address_line2"]
        city = cleaned["city"]
        pincode = cleaned["pincode"]

        # stock validation before ordering
        for item in items:
            variant = item["variant"]
            qty = item["quantity"]

            if variant.stock < qty:
                messages.error(
                    request,
                    f"Only {variant.stock} left for {variant.product.title} ({variant.color})."
                )
                return redirect("cart")

        # atomically create order, items, and reduce stock
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                customer_name=name,
                phone=phone,
                address_line1=address1,
                address_line2=address2,
                city=city,
                pincode=pincode,
                total=total,
                status="pending",
                payment_method="cod",       # for now always COD
                payment_status="pending",   # not yet collected
            )

            for item in items:
                OrderItem.objects.create(
                    order=order,
                    variant=item["variant"],
                    quantity=item["quantity"],
                    price=item["variant"].price,
                )

            for item in items:
                variant = item["variant"]
                variant.stock -= item["quantity"]
                variant.save()

        request.session["cart"] = {}
        return redirect("order_thank_you", pk=order.pk)

    else:
        # GET request: empty form
        form = CheckoutForm()

    context = {
        "items": items,
        "total": total,
        "form": form,
    }
    return render(request, "siteapp/checkout.html", context)



def order_thank_you(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, "siteapp/order_thank_you.html", {"order": order})


def remove_from_cart(request):
    if request.method != "POST":
        return redirect("cart")

    variant_id = request.POST.get("variant_id")
    if not variant_id:
        return redirect("cart")

    variant_id = str(variant_id)
    cart = request.session.get("cart", {})

    if variant_id in cart:
        del cart[variant_id]
        request.session["cart"] = cart
        messages.success(request, "Item removed from cart.")

    return redirect("cart")


def clear_cart(request):
    if request.method != "POST":
        return redirect("cart")

    request.session["cart"] = {}
    messages.success(request, "Cart cleared.")
    return redirect("cart")


def update_cart_quantity(request):
    if request.method != "POST":
        return redirect("cart")

    variant_id = request.POST.get("variant_id")
    action = request.POST.get("action")

    if not variant_id or action not in ["inc", "dec"]:
        return redirect("cart")

    variant_id = str(variant_id)
    cart = request.session.get("cart", {})

    if variant_id not in cart:
        return redirect("cart")

    current_qty = cart[variant_id]
    variant = get_object_or_404(ProductVariant, id=variant_id)

    if action == "inc":
        # don't allow exceeding stock
        if current_qty + 1 > variant.stock:
            messages.error(
                request,
                f"Only {variant.stock} piece(s) available for {variant.product.title}."
            )
            return redirect("cart")

        cart[variant_id] = current_qty + 1

    elif action == "dec":
        # if quantity goes to 0, remove item
        if current_qty <= 1:
            del cart[variant_id]
            messages.success(request, "Item removed from cart.")
        else:
            cart[variant_id] = current_qty - 1

    request.session["cart"] = cart
    return redirect("cart")


def order_track(request):
    order = None

    if request.method == "POST":
        order_id = request.POST.get("order_id")
        phone = request.POST.get("phone", "").strip()

        if not (order_id and phone):
            messages.error(request, "Please enter both order ID and phone number.")
            return redirect("order_track")

        try:
            order = Order.objects.get(id=order_id, phone=phone)
        except Order.DoesNotExist:
            messages.error(request, "No order found for that ID and phone number.")
            return redirect("order_track")

    return render(request, "siteapp/order_track.html", {"order": order})


def category_page(request, slug):
    category = get_object_or_404(Category, slug=slug)
    categories = Category.objects.all()
    products = Product.objects.filter(active=True, category=category).order_by("-created_at")

    q = request.GET.get("q", "").strip()
    if q:
        products = products.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q)
        )

    context = {
        "products": products,
        "categories": categories,
        "current_category": category,
        "current_search": q,
    }
    return render(request, "siteapp/home.html", context)


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # uses UserCreationForm’s secure logic
            login(request, user)
            messages.success(request, "Account created and logged in.")
            return redirect("home")
    else:
        form = SignUpForm()

    return render(request, "siteapp/signup.html", {"form": form})


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "siteapp/my_orders.html", {"orders": orders})
