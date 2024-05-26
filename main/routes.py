"""
Routes of the application
"""
# Import statements
import os

from flask import render_template, redirect, url_for, flash, request, send_from_directory, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename

from main import app, db
from main.forms import RegisterForm, LoginForm, ChangePasswordForm, ShopItemsForm, OrderForm
from main.models import Product, Customer, Cart, Order


class CustomException(Exception):
    """Class for custom exceptions"""


# Constants
ACCESS_DENIED_HTML = 'access-denied.html'
ADMIN_EMAIL = 'admin@admin.com'
API_PUBLISHABLE_KEY = os.getenv("API_PUBLISHABLE_KEY")
API_TOKEN = os.getenv("API_TOKEN")
# Creating the tables if they don't exist
with app.app_context():
    try:
        db.create_all()
    except SQLAlchemyError:
        print("Tables already exist")


@app.route('/media/<path:filename>')
def get_image(filename):
    """
    Function to load the images on the webpage
    :param filename: The name of the file
    :return: The image
    """
    # Get the images from the media directory
    return send_from_directory('../media', filename)


@app.route('/')
@app.route('/home')
def home_page():
    """
    Home Api

    Description:
        This loads the home page for the application showing all the available products

    Response:
        If successful, returns 200 status code

    Example request:
        GET http://127.0.0.1:5000/

    """
    items = Product.query.all()
    return render_template("home.html",
                           items=items,
                           cart=Cart.query.filter_by(customer_id=current_user.id).all()
                           if current_user.is_authenticated else [])  # Get the users cart


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    """
    Register Api

    Description:
        This loads the register page for the application

    Response:
        If successful, returns 302 status code

    Example request:
        POST http://127.0.0.1:5000/register

    Request Body:
        csrf_token: IjBlOTcwMzZiYWZjNGY5MjUwZWYyM2I4NzY2NGVmMjFlNzZjM2FhOTIi.ZlOQgA.SAXfqP3Ja7yjE3bG1V3azh4r5oU

        username: admin

        email: admin@admin.com

        password: 123456

        confirm_password: 123456

        submit: Create Account

    How it works:
        First the register page is loaded

        Then the user inputs credentials and submits the form

        Then if the registration is successful you are redirected to the home page

        Otherwise the user is alert there has been an error creating the account
    """
    form = RegisterForm()
    # If the validation checks have passed
    if form.validate_on_submit():
        # Retrieve the data from the registration form
        username = form.username.data
        email = form.email.data
        password = form.password.data
        confirm_password = form.confirm_password.data

        if password == confirm_password:
            # Use the data from the form to create a new user
            customer = Customer()
            customer.username = username
            customer.email = email
            customer.password = confirm_password
            # Add new user to the customers table
            db.session.add(customer)
            db.session.commit()
            # Automatically log in the user after registering
            login_user(customer)
            # Notify the user they have created an account and logged in
            flash(
                f'Account created successfully! You are now logged in as {customer.username}',
                category='success'
            )
            # Redirect the user to the home page after logging in
            return redirect(url_for('home_page'))
    # If there are errors alert the user
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')
    # Load the register page
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    """
    Login Api

    Description:
        Loads the login page for the application and logs in the user

    Response:
        If successful, returns 302 status code

    Example request:
        POST http://127.0.0.1:5000/login

    Request Body:
        csrf_token: IjBlOTcwMzZiYWZjNGY5MjUwZWYyM2I4NzY2NGVmMjFlNzZjM2FhOTIi.ZlOQgA.SAXfqP3Ja7yjE3bG1V3azh4r5oU

        email: admin@admin.com

        password: 123456

        submit: Login

    How it works:
        First the login page is loaded

        Then the user inputs credentials and submits the form

        Then if the login is successful you are redirected to the home page

        Otherwise the user is alert there has been an error logging into the account
    """
    form = LoginForm()
    # If the validation checks have passed
    if form.validate_on_submit():
        # Login the user if the credentials are correct
        attempted_user = Customer.query.filter_by(email=form.email.data).first()
        if attempted_user and attempted_user.verify_password(password=form.password.data):
            login_user(attempted_user)
            # Alter the user they are logged in
            flash(f'You are now logged in as: {attempted_user.username}', category='success')
            # Redirect to the home page
            return redirect(url_for('home_page'))
        # Alert the user to the failed login attempt
        flash("Email and password don't match a valid user", category='danger')
    # Load the login page
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout_page():
    """
    Logout Api

    Description:
        This logs the user out

    Response:
        If successful, returns 302 status code

    Example request:
        GET http://127.0.0.1:5000/logout

    """
    # Logout the user
    logout_user()
    # Alert the user they have been logged out
    flash('You are now logged out', category='info')
    # Redirect to the home page
    return redirect(url_for('home_page'))


@app.route('/profile/<int:customer_id>')
@login_required
def profile_page(customer_id):
    """
    Profile Api

    Description:
        This loads the user's profile page

    Parameters:
        customer_id: The users id

    Response:
        If successful, returns 200 status code

    Example request:
        GET http://127.0.0.1:5000/profile/1

    """
    # Verify the customer and display their profile page
    customer = Customer.query.get(customer_id)
    if current_user.id == customer_id:
        return render_template('profile.html', customer=customer)
    # If unable to verify customer redirect to access denied page
    return render_template(ACCESS_DENIED_HTML)


@app.route('/change_password/<int:customer_id>', methods=["GET", "POST"])
@login_required
def change_password_page(customer_id):
    """
    Change Password Api

    Description:
        Updates the user's password

    Parameters:
        customer_id: The users id

    Response:
        If successful, returns 302 status code

    Example request:
        POST http://127.0.0.1:5000/change_password/1

    Request Body:
        csrf_token: IjBlOTcwMzZiYWZjNGY5MjUwZWYyM2I4NzY2NGVmMjFlNzZjM2FhOTIi.ZlOQgA.SAXfqP3Ja7yjE3bG1V3azh4r5oU

        current_password: 123456

        new_password: 12345678

        confirm_password: 12345678

        submit: Update password

    How it works:
        First the change password page is loaded

        Then the user inputs their current password and the password they want to change it to and submits the form

        Then if the validation checks pass the password is updated, and they are redirected to the profile page

        Otherwise the user is alert there has been an error updating their password
    """
    form = ChangePasswordForm()
    customer = Customer.query.get(customer_id)
    # If validation checks have passed
    if form.validate_on_submit():
        # Retrieve data from form
        current_password = form.current_password.data
        new_password = form.new_password.data
        confirm_password = form.confirm_password.data
        # Verify the customer
        if customer.verify_password(current_password):
            # Check the new password
            if new_password == confirm_password:
                customer.password = confirm_password
                # Update the password
                db.session.commit()
                # Alert the user the password has been changed
                flash('Password updated', category='success')
                # Redirect the user to there profile page
                return redirect(url_for('profile_page', customer_id=customer_id))
            # Alert the user if the new passwords don't match
            flash('New passwords do not match', category='danger')
        else:
            # Alert the user if the current password is incorrect
            flash('Current password is incorrect', category='danger')
    # Load the change password page if the user has been verified
    if current_user.id == customer_id:
        return render_template('change-password.html', form=form)
    # Load the access denied page if the user couldn't be verified
    return render_template(ACCESS_DENIED_HTML)


@app.route('/create_product', methods=['GET', 'POST'])
@login_required
def create_product():
    """
        Create product API

        Description:
            Adds a new product to the list of available products

        Response:
            If successful, returns 200 status code

        Example request:
            POST http://127.0.0.1:5000/create_product

        Request Body:
            csrf_token: IjBlOTcwMzZiYWZjNGY5MjUwZWYyM2I4NzY2NGVmMjFlNzZjM2FhOTIi.ZlOQgA.SAXfqP3Ja7yjE3bG1V3azh4r5oU

            product_name: Apple Watch Ultra

            price: 800

            quantity: 1

            description: Apple Watch

            product_image: AppleWatch.jpg

            add_product: Add Product

        How it works:
            First the add product page is loaded

            Then the user inputs the values and submits the form

            Then if the validation checks pass the product is created

            Otherwise the user is alert there has been an error updating their password
    """
    # Verifies the user is the administrator
    if current_user.email == ADMIN_EMAIL:
        form = ShopItemsForm()
        # If validation checks have passed
        if form.validate_on_submit():
            # Create a new product using the data from the form
            product_name = form.product_name.data
            price = form.price.data
            quantity = form.quantity.data
            description = form.description.data
            file = form.product_image.data
            # Convert the file name to a secure file name
            file_name = secure_filename(file.filename)
            product_image = f'./media/{file_name}'
            file.save(product_image)
            new_product = Product(
                name=product_name,
                price=price,
                quantity=quantity,
                description=description,
                product_image=product_image
            )
            # Add new product to the products table
            db.session.add(new_product)
            db.session.commit()
            # Alert the user thst the new product have been created
            flash(f'{product_name} Added Successfully', category='success')
            # Display the create product page
            return render_template('create-product.html', form=form)
        # If there are errors, alert the user
        if form.errors != {}:
            for err_msg in form.errors.values():
                flash(f'There was an error with adding a product: {err_msg}', category='danger')
        # Display the create product page
        return render_template('create-product.html', form=form)
    # Display the access denied page if the user is not an administrator
    return render_template(ACCESS_DENIED_HTML)


@app.route('/view-shop-items', methods=['GET', 'POST'])
@login_required
def shop_items():
    """
    Shop Items Api

    Description:
        This loads the shop items page for the application allowing administrators to manage shop items

    Response:
        If successful, returns 200 status code

    Example request:
        GET http://127.0.0.1:5000/view-shop-items

    """
    # Verify the user is an administrator
    if current_user.email == ADMIN_EMAIL:
        # Get all items and display them on the page in a table
        items = Product.query.order_by(Product.date_added).all()
        return render_template('shop_items.html', items=items)
    # Display the access denied page if the user in not an administrator
    return render_template(ACCESS_DENIED_HTML)


@app.route('/update-item/<int:product_id>', methods=['GET', 'POST'])
@login_required
def update_item(product_id):
    """
    Update Items Api

    Description:
        This loads the update items page for the application allowing administrators to update an item

    Parameters:
        product_id: The id of the product

    Response:
        If successful, returns 302 status code

    Example request:
        POST http://127.0.0.1:5000/update-item/1

    How it works:
        First the update item page is loaded
        Then the user inputs the values and submits the form
        Then if the validation checks pass the product is update
        Otherwise the user is alert there has been an error updating the product
    """
    # Check the user is an administrator
    if current_user.email == ADMIN_EMAIL:
        form = ShopItemsForm()
        # Default the values in the form to the product you're updating
        item_to_update = Product.query.get(product_id)
        form.product_name.render_kw = {'placeholder': item_to_update.name}
        form.price.render_kw = {'placeholder': item_to_update.price}
        form.quantity.render_kw = {'placeholder': item_to_update.quantity}
        form.description.render_kw = {'placeholder': item_to_update.description}
        # If the validation checks have passed
        if form.validate_on_submit():
            # update the product using the data from the form
            product_name = form.product_name.data
            quantity = form.quantity.data
            description = form.description.data
            price = form.price.data
            file = form.product_image.data
            file_name = secure_filename(file.filename)
            file_path = f'./media/{file_name}'
            file.save(file_path)
            Product.query.filter_by(id=product_id).update({
                "name": product_name,
                "price": price,
                "quantity": quantity,
                "description": description,
                "product_image": file_path
            })
            # Update the product in the database
            db.session.commit()
            # Alert the user the product has been updated
            flash(f'{product_name} Updated Successfully', category='success')
            # Redirect the user after updating the product
            return redirect(url_for('shop_items'))
        # If there are errors, alert the user
        if form.errors != {}:
            for err_msg in form.errors.values():
                flash(f'There was an error with updating a product: {err_msg}', category='danger')
        # Display the update item page
        return render_template('update_item.html', form=form)
    # Display the access denied page if a non-administrator attempts to access the update items page
    return render_template(ACCESS_DENIED_HTML)


@app.route('/delete-item/<int:product_id>', methods=['GET', 'DELETE'])
@login_required
def delete_item(product_id):
    """
    Delete Item Api

    Description:
        This removes an item from the website

    Parameters:
        product_id: The id of the product

    Response:
        If successful, returns 200 status code

    Example request:
        DELETE http://127.0.0.1:5000/delete-item/1

    """
    # Verify the user is the administrator
    if current_user.email == ADMIN_EMAIL:
        # Delete the item from the database
        item_to_delete = Product.query.get(product_id)
        db.session.delete(item_to_delete)
        db.session.commit()
        # Alert the user the item has been deleted
        flash('Item Deleted Successfully', category='success')
        # Redirect the user to the manage product page
        return redirect(url_for('shop_items'))
    # Display the access denied page if a non-administrator attempts to delete a product
    return render_template(ACCESS_DENIED_HTML)


@app.route('/add-to-cart/<int:product_id>', methods=['GET', 'POST'])
@login_required
def add_to_cart(product_id):
    """
    Add to cart Api

    Description:
        This adds an item to the cart

    Parameters:
        product_id: The id of the product

    Response:
        If successful, returns 302 status code

    Example request:
        GET http://127.0.0.1:5000/add-to-cart/1
    """
    # Get the product
    item_to_add = Product.query.get(product_id)
    # Check if the item is already in your cart
    item_exists = Cart.query.filter_by(product_id=product_id, customer_id=current_user.id).first()
    # If the item is already in your cart increase the quantity
    if item_exists:
        item_exists.quantity += 1
        db.session.commit()
        # Alert the user the item has been added to their cart
        flash('Item Added Successfully', category='success')
        return redirect(request.referrer)
    # If the item is not already in the cart add it to the cart
    new_cart_item = Cart()
    new_cart_item.quantity = 1
    new_cart_item.product_id = item_to_add.id
    new_cart_item.customer_id = current_user.id
    # Update the database
    db.session.add(new_cart_item)
    db.session.commit()
    # Alert the user the item has been added to their cart
    flash(f'{new_cart_item.product.name} Added Successfully', category='success')
    return redirect(request.referrer)


@app.route('/increase-quantity', methods=['GET'])
@login_required
def increase_quantity():
    """
    Increase quantity Api

    Description:
        This increases the quantity of a product in your cart

    Response:
        If successful, returns 200 status code

    Example request:
        GET http://127.0.0.1:5000/increase-quantity?cart_id=1

    How it works:
        When the plus button is clicked the quantity is increased
    """
    # Get the cart for the user and increase the quantity of the item
    cart_id = request.args.get('cart_id')
    cart_item = Cart.query.get(cart_id)
    cart_item.quantity += 1
    # Update the database
    db.session.commit()
    # Update the values in the cart
    cart = Cart.query.filter_by(customer_id=current_user.id).all()
    amount = 0
    for item in cart:
        amount += item.product.price * item.quantity
    data = {
        'quantity': cart_item.quantity,
        'amount': amount,
    }
    return jsonify(data)


@app.route('/decrease-quantity', methods=['GET'])
@login_required
def decrease_quantity():
    """
    Decreased quantity Api

    Description:
        This decreases the quantity of a product in your cart

    Response:
        If successful, returns 200 status code

    Example request:
        GET http://127.0.0.1:5000/decrease-quantity?cart_id=1

    How it works:
        When the minus button is clicked, the quantity is decreased
    """
    # Get the cart for the user and increase the quantity of the item
    cart_id = request.args.get('cart_id')
    cart_item = Cart.query.get(cart_id)
    cart_item.quantity -= 1
    # Update the database
    db.session.commit()
    # Update the values in the cart
    cart = Cart.query.filter_by(customer_id=current_user.id).all()
    amount = 0
    for item in cart:
        amount += item.product.price * item.quantity
    data = {
        'quantity': cart_item.quantity,
        'amount': amount,
    }
    return jsonify(data)


@app.route('/remove-from-cart', methods=['GET'])
@login_required
def remove_from_cart():
    """
    Remove from cart Api

    Description:
        This removing an item from your cart

    Response:
        If successful, returns 200 status code

    Example request:
        GET http://127.0.0.1:5000/remove-from-cart?cart_id=1

    How it works:
        When the remove button is clicked, the item is removed from your cart
    """
    # Get the cart for the user and remove the item from the cart
    cart_id = request.args.get('cart_id')
    cart_item = Cart.query.get(cart_id)
    # Update the database
    db.session.delete(cart_item)
    db.session.commit()
    # Update the values in the cart
    cart = Cart.query.filter_by(customer_id=current_user.id).all()
    amount = 0
    for item in cart:
        amount += item.product.price * item.quantity
    data = {
        'quantity': cart_item.quantity,
        'amount': amount,
    }
    return jsonify(data)


@app.route('/cart')
@login_required
def show_cart():
    """
    Show cart Api

    Description:
        This shows the items in your cart

    Response:
        If successful, returns 200 status code

    Example request:
        GET http://127.0.0.1:5000/cart
    """
    # Get the items in the cart
    cart = Cart.query.filter_by(customer_id=current_user.id).all()
    # Calculate the price
    amount = 0
    for item in cart:
        amount += item.product.price * item.quantity
    # Display the cart page
    return render_template('cart.html', cart=cart, amount=amount)


@app.route('/place-order')
@login_required
def place_order():
    """
    Place order Api

    Description:
        This places an order

    Response:
        If successful, returns 200 status code

    Example request:
        GET http://127.0.0.1:5000/place-order
    """
    # Get the items in the cart
    customer_cart = Cart.query.filter_by(customer_id=current_user.id)
    # Check the cart isn't empty
    if customer_cart:
        try:
            # Calculate the total
            total = 0
            for item in customer_cart:
                total += item.product.price * item.quantity
            for item in customer_cart:
                # Create order
                new_order = Order()
                new_order.quantity = item.quantity
                new_order.price = total
                new_order.status = 'Pending'
                new_order.payment_id = 1
                new_order.product_id = item.product_id
                new_order.customer_id = item.customer_id
                # Update database
                db.session.add(new_order)
                # Update stock
                product = Product.query.get(item.product_id)
                if product.quantity - item.quantity >= 0:
                    product.quantity -= item.quantity
                    db.session.delete(item)
                    db.session.commit()
                else:
                    # Raise exception if the item isn't available
                    raise CustomException('Item is not available')
            # Alert the user their order has been placed
            flash('Order Placed Successfully', category='success')
            # Redirect the user to order history page
            return redirect(url_for('my_orders'))
        except CustomException:
            # Alert the user if the order couldn't be placed
            flash('Order not placed', category='danger')
            # Redirect the user to the home page
            return redirect(url_for('home_page'))


@app.route('/orders')
@login_required
def my_orders():
    """
    Order history Api

    Description:
        This shows a users order history

    Response:
        If successful, returns 200 status code

    Example request:
        GET http://127.0.0.1:5000/orders
    """
    # Get the users order history
    orders = Order.query.filter_by(customer_id=current_user.id).all()
    # Display users order history page
    return render_template('orders.html', orders=orders)


@app.route('/search', methods=['GET', 'POST'])
def search():
    """
    Search Api

    Description:
        Loads the search pages and returns items matching the search criteria

    Response:
        If successful, returns 200 status code

    Example request:
        POST http://127.0.0.1:5000/search

    Request Body:
        search: Apple Watch
        search_btn:

    How it works:
        First the search page is loaded

        Then the user inputs the search term and clicks the search_btn

        Then the search results are displayed
    """
    if request.method == 'POST':
        # Get the search query from the form
        search_query = request.form.get('search')
        # Check the search query against items in the database
        items = Product.query.filter(Product.name.ilike(f'%{search_query}%')).all()
        # Display items matching the search query
        return render_template('search.html', items=items,
                               cart=Cart.query.filter_by(customer_id=current_user.id).all()
                               if current_user.is_authenticated else [])
    # Load the search page
    return render_template('search.html')


@app.route('/view-orders')
@login_required
def order_view():
    """
    Manage orders Api

    Description:
        This loads the manage orders page

    Response:
            If successful, returns 200 status code

    Example request:
        GET http://127.0.0.1:5000/view-orders

    """
    # Verify the user is the administrator
    if current_user.email == ADMIN_EMAIL:
        # Get a list of all orders and display them on screen
        orders = Order.query.all()
        return render_template('view_orders.html', orders=orders)
    # Display the access denied page if a non-administrator attempts to view the orders page
    return render_template(ACCESS_DENIED_HTML)


@app.route('/update-order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def update_order(order_id):
    """
    Update order status Api

    Description:
        This updates the status of an order

    Parameters:
        order_id: The id of the order

    Response:
        If successful, returns 302 status code

    Example request:
        POST http://127.0.0.1:5000/update-order/1

    Request Body:
        status: "Delivered"

    How it works:
        First the update order page is loaded

        Then the user fills out and submits the form

        Then if the update is successful you are redirected to the manage order page

        Otherwise the user is alert there has been an error updating an order
    """
    # Verify the user is an administrator
    if current_user.email == ADMIN_EMAIL:
        form = OrderForm()

        order = Order.query.get(order_id)
        # If the validation checks pass
        if form.validate_on_submit():
            # Update the status of the order using the data from the form
            status = form.order_status.data
            order.status = status
            # Update the database
            db.session.commit()
            # Alert the user the order status has been updated
            flash(f'Order {order_id} Updated successfully', category='success')
            # Redirect the user to the order view page
            return redirect(url_for('order_view'))
        # Alert the user the order status couldn't be updated
        flash(f'Order {order_id} not updated', category='danger')
        # Display the update order page
        return render_template('order_update.html', form=form)
    # Display the access denied page if the user is not an administrator
    return render_template(ACCESS_DENIED_HTML)


@app.route('/customers')
@login_required
def display_customers():
    """
    Manage users Api

    Description:
        This loads the manage users page

    Response:
            If successful, returns 200 status code

    Example request:
        GET http://127.0.0.1:5000/customers

    """
    # Verify the user is an administrator
    if current_user.email == ADMIN_EMAIL:
        # Get a list of users and display it to the user
        customers = Customer.query.all()
        return render_template('customers.html', customers=customers)
    # Display the access denied page if the user is not an administrator
    return render_template(ACCESS_DENIED_HTML)


@app.route('/customers/<int:customer_id>', methods=['GET', 'DELETE'])
@login_required
def delete_customer(customer_id):
    """
    Delete user Api

    Description:
        This deletes a user from the website

    Parameters:
        customer_id: The id of the user

    Response:
        If successful, returns 200 status code

    Example request:
        DELETE http://127.0.0.1:5000/customers/1

    """
    # Verify the user is an administrator
    if current_user.email == ADMIN_EMAIL:
        # Delete the customer and update the database
        account_to_delete = Customer.query.get(customer_id)
        db.session.delete(account_to_delete)
        db.session.commit()
        # Alert the user the account has been deleted
        flash(
            f"The account with the email '{account_to_delete.email}' has been deleted",
            category='success')
        # Redirect the user to the display customers page
        return redirect(url_for('display_customers'))
    # Display the access denied page if the user is not an administrator
    return render_template(ACCESS_DENIED_HTML)


def common_passwords():
    """
    Function for reading the common passwords for the common passwords file
    :return: A list of common passwords
    """
    # Read the list of common passwords from the common passwords file
    script_dir = os.path.dirname(__file__)
    script_dir.replace("\\", '/')
    with open(f'{script_dir}/common_passwords.txt', 'r', encoding="utf-8") as f:
        most_common_passwords = f.read().split('\n')
    return most_common_passwords


@app.route('/attacker/dictionary-attack', methods=['GET', 'POST'])
def dictionary_attack():
    """
    Dictionary attack Api

    Description:
        This performs a dictionary attack on the administrator

    Response:
        If successful, returns 302 status code

    Example request:
        GET http://127.0.0.1:5000/attacker/dictionary-attack

    How it works:
        It checks a list common password and if it finds a match alerts the attacker to the admins password
    """
    app.config['WTF_CSRF_ENABLED'] = False
    # Check the administrator's password is in the list of common passwords
    for password in common_passwords():
        attempted_user = Customer.query.filter_by(email='admin@admin.com').first()
        if attempted_user and attempted_user.verify_password(password=password):
            # Display the password to the attacker
            flash(f"Password is {password}'", category='success')
            # Login the user
            login_user(attempted_user)
            # Redirect the user to the home page
            return redirect(url_for('home_page'))
