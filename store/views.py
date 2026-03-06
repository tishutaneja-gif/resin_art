from django.shortcuts import render, redirect
import pymysql
from django.contrib.auth import logout
from django.shortcuts import redirect
import os
import uuid
from django.conf import settings

def logout_view(request):
    logout(request)
    return redirect('admin_login')

def dbconnections():
    """
    Establish a direct MySQL database connection.
    Returns both the connection and a cursor object.
    """
    db = pymysql.connect(
        host="localhost",       # your database host
        user="root",            # your database username
        password="Tishu@4789",  # your database password
        database="resin_store", # your database name
        port=3306,              # default MySQL port
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )
    cur = db.cursor()
    return db, cur


def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


def products(request):
    db, cur = dbconnections()
    try:
        cur.execute("SELECT id, title, description, price, image_url, category FROM products")
        products = cur.fetchall()  # now each row is a dict like {"id": 1, "title": "...", "price": 1200, ...}
    except Exception as e:
        print("❌ Error fetching products:", e)
        products = []
    finally:
        db.close()

    return render(request, 'products.html', {'products': products})


def product_detail(request, pid):
    db, cur = dbconnections()
    try:
        cur.execute("SELECT * FROM products WHERE id = %s", [pid])
        product = cur.fetchone()
    except Exception as e:
        print("❌ Error fetching product details:", e)
        product = None
    finally:
        db.close()
    return render(request, 'product_detail.html', {'product': product})


def admin_login(request):
    error = ""
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        db, cur = dbconnections()
        try:
            cur.execute("SELECT * FROM admins WHERE username=%s AND password=%s", [username, password])
            admin = cur.fetchone()
        except Exception as e:
            print("❌ Error during admin login:", e)
            admin = None
        finally:
            db.close()

        if admin:
            return redirect('admin_dashboard')
        else:
            error = "Invalid credentials"

    return render(request, 'admin_login.html', {'error': error})


def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')


def add_product(request):
    if request.method == "POST":
        title = request.POST.get("title")
        desc = request.POST.get("description")
        price = request.POST.get("price")
        category = request.POST.get("category")

        image_file = request.FILES.get("image_file")

        # Handle image upload
        if image_file:
            # Create unique name
            file_name = f"{uuid.uuid4().hex}{os.path.splitext(image_file.name)[1]}"
            product_folder = os.path.join(settings.MEDIA_ROOT, "products")
            os.makedirs(product_folder, exist_ok=True)

            full_path = os.path.join(product_folder, file_name)
            with open(full_path, "wb+") as f:
                for chunk in image_file.chunks():
                    f.write(chunk)

            # Path stored in DB
            image_db_path = f"products/{file_name}"
        else:
            image_db_path = ""

        # Correctly use dbconnections()
        db, cur = dbconnections()
        try:
            cur.execute("""
                INSERT INTO products (title, description, price, image_url, category)
                VALUES (%s, %s, %s, %s, %s)
            """, (title, desc, price, image_db_path, category))
            db.commit()
        except Exception as e:
            print("❌ Error inserting product:", e)
        finally:
            db.close()

    return redirect("products")



def products_by_category(request, cat):

    db, cur = dbconnections()

    try:
        cur.execute(
            "SELECT id, title, description, price, image_url, category FROM products WHERE category=%s",
            [cat]
        )
        products = cur.fetchall()

    except Exception as e:
        print("❌ Error:", e)
        products = []

    finally:
        db.close()

    return render(request, "products.html", {"products": products})    