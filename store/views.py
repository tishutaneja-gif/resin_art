from django.shortcuts import render, redirect
import pymysql
from django.contrib.auth import logout
from django.shortcuts import redirect
import os
import uuid
from django.conf import settings
from django.http import HttpResponse
from .db import get_connection
from django.db import connection

def setup_database(request):

    conn = get_connection()
    cursor = conn.cursor()

    # CREATE ADMINS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50),
        password VARCHAR(100)
    )
    """)

    # INSERT ADMIN VALUE
    cursor.execute("""
    INSERT INTO admins (id, username, password)
    VALUES (1, 'Tishu01', 'Resinart@123')
    """)

    # CREATE PRODUCTS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(200),
        description TEXT,
        price FLOAT,
        image_url VARCHAR(255),
        category VARCHAR(100)
    )
    """)

    # INSERT PRODUCTS
    cursor.execute("""
    INSERT INTO products (id, title, description, price, image_url, category)
    VALUES
    (1,'nature..','waterfall..',3800,'products/ec41e7e24c4b481b99126fd5d6fe7e36.jpg','painting'),
    (2,'painting..','it is about wildlife..',5600,'products/a110871205d349d19257b3c54fc682e0.jpg','painting')
    """)

    conn.commit()
    cursor.close()
    conn.close()

    return HttpResponse("Database tables created and values inserted successfully")
def logout_view(request):
    logout(request)
    return redirect('admin_login')



def dbconnections():
    """
    Use Django's configured database connection (PostgreSQL on Render).
    Returns the connection and cursor.
    """
    cur = connection.cursor()
    db = connection
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


