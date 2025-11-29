
# 🧵 Niti Satika – Saree E-Commerce Store (Django)

Niti Satika is a fully functional saree e-commerce web application built using **Django**, designed as a real production-ready project for a boutique saree shop.  
It includes product catalog, variants, cart, checkout, order tracking, and a polished UI with a premium gold–ivory theme.

---

## ⭐ Features

### 🛍 Product & Catalog
- Product listing with categories  
- Product detail page  
- Single-color sarees  
- Variants: **with blouse** / **without blouse**  
- Individual pricing for variants  
- Stock control  

### 🛒 Cart & Checkout
- Add to cart (only if logged in)  
- Increase / decrease quantity  
- Prevent adding more than available stock  
- Full checkout flow (name, phone, address, pincode, city)  
- Order summary & confirmation page  

### 📦 Order Tracking
- Track order using **Order ID + Phone number**  
- View items, amounts, and live status  
- Safe implementation (no data leaks)

### 👤 User System
- Login / Logout / Signup  
- Custom secure signup form  
- Logged-in users can view **My Orders**  
- All order & cart operations require authentication  

### 🛠 Admin Panel (Django Admin)
- Manage products, categories, variants  
- Inline variant editing  
- Stock updates  
- Order management + status updates  
- Actions: Confirmed / Packed / Shipped / Delivered / Cancelled  

### 📥 Bulk Import (CSV)
Includes a management command:
```

python manage.py import_products

```
Automatically:
- Reads `data/products.csv`  
- Creates product  
- Creates both variants  
- Fills stock  
- Avoids duplicates  

---

## 📁 Project Structure

```

Saree_site/
│── siteapp/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/siteapp/
│   ├── static/siteapp/style.css
│   ├── data/products.csv
│   └── management/commands/import_products.py
│── Saree_site/
│── manage.py

````

---

## 🚀 Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/niti-satika.git
cd niti-satika
````

### 2. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Database migrations

```bash
python manage.py migrate
```

### 5. Create admin user

```bash
python manage.py createsuperuser
```

### 6. Import sample saree products (optional)

```bash
python manage.py import_products
```

### 7. Run development server

```bash
python manage.py runserver
```

---

## 🔐 Security Features

* CSRF protection
* Auth-protected cart/checkout
* Server-side stock validation
* Atomic transactions for order creation
* Strict POST-only actions
* Safe order tracking

---

## 🎨 Frontend & UX

* Modern premium look with gold/ivory theme
* Responsive grid layout
* Mobile-friendly
* Clean Tailwind + custom CSS
* Smooth hover interactions

---

## 🧭 Future Enhancements

* Razorpay/PhonePe payments
* Coupons / offers
* Address book for saved addresses
* Wishlist
* Product reviews
* Delivery charges

---

## 👤 Author

**Akash Jolly**
Built as a production-ready real project for a saree business.



