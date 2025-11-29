from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model


class Category(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("category_page", args=[self.slug])


class Product(models.Model):
    """
    A saree product. Variants handle colors / blouse options.
    """

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    description = models.TextField(blank=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )

    featured_image = models.ImageField(upload_to="products/")  # saree photo

    base_price = models.DecimalField(max_digits=10, decimal_places=2)

    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("product_detail", args=[self.slug])


class ProductVariant(models.Model):
    """
    Variant of a saree:
    - different color
    - with/without blouse
    - can have different price / stock
    """

    BLOUSE_CHOICES = [
        ("with_blouse", "With Blouse"),
        ("without_blouse", "Without Blouse"),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants",
    )

    sku = models.CharField(
        max_length=64,
        blank=True,
        help_text="Internal code for this variant (optional).",
    )

    color = models.CharField(
        max_length=64,
        blank=True,
        help_text="e.g. Red, Blue, Green",
    )

    blouse_option = models.CharField(
        max_length=32,
        choices=BLOUSE_CHOICES,
        default="with_blouse",
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Leave same as base price if no change.",
    )

    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        bits = [self.product.title]
        if self.color:
            bits.append(self.color)
        blouse_label = dict(self.BLOUSE_CHOICES).get(self.blouse_option, "")
        if blouse_label:
            bits.append(blouse_label)
        return " – ".join(bits)

User = get_user_model()


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("packed", "Packed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("cod", "Cash on Delivery"),
        # later you can add "online"
    ]

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    customer_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    # 🔹 NEW FIELDS:
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default="cod",
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE,
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
    )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per item at time of order.",
    )

    def __str__(self):
        return f"{self.variant} x {self.quantity}"