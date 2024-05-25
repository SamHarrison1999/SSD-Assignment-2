from flask import render_template, redirect, url_for, flash, request, send_from_directory, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from intasend import APIService
from werkzeug.utils import secure_filename

from main import app, db
from main.forms import RegisterForm, LoginForm, ChangePasswordForm, ShopItemsForm, OrderForm
from main.models import Product, Customer, Cart, Order


class CustomException(Exception):
    pass


ACCESS_DENIED_HTML = 'access-denied.html'
ADMIN_EMAIL = 'admin@admin.com'
API_PUBLISHABLE_KEY = 'ISPubKey_test_e26cdffa-f89c-41dd-a0d6-d16d1803ff34'
API_TOKEN = 'ISSecretKey_test_ec8f48a5-1e0a-4aeb-ae73-6b403a41ae32'
with app.app_context():
    db.create_all()


@app.route('/media/<path:filename>')
def get_image(filename):
    return send_from_directory('../media', filename)


@app.route('/')
@app.route('/home')
def home_page():
    items = Product.query.all()
    return render_template("home.html",
                           items=items,
                           cart=Cart.query.filter_by(customer_id=current_user.id).all()
                           if current_user.is_authenticated else [])


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        confirm_password = form.confirm_password.data

        if password == confirm_password:
            customer = Customer()
            customer.username = username
            customer.email = email
            customer.password = confirm_password
            db.session.add(customer)
            db.session.commit()
            login_user(customer)
            flash(
                f'Account created successfully! You are now logged in as {customer.username}',
                category='success'
            )
        return redirect(url_for('home_page'))
    if form.errors != {}:  # If there are errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = Customer.query.filter_by(email=form.email.data).first()
        if attempted_user and attempted_user.verify_password(password=form.password.data):
            login_user(attempted_user)
            flash(f'You are now logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('home_page'))
        flash("Email and password don't match a valid user", category='danger')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout_page():
    logout_user()
    flash('You are now logged out', category='info')
    return redirect(url_for('home_page'))


@app.route('/profile/<int:customer_id>')
@login_required
def profile_page(customer_id):
    customer = Customer.query.get(customer_id)
    if current_user.id == customer_id:
        return render_template('profile.html', customer=customer)
    return render_template(ACCESS_DENIED_HTML)


@app.route('/change_password/<int:customer_id>', methods=["GET", "POST"])
@login_required
def change_password_page(customer_id):
    form = ChangePasswordForm()
    customer = Customer.query.get(customer_id)
    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data
        confirm_password = form.confirm_password.data
        if customer.verify_password(current_password):
            if new_password == confirm_password:
                customer.password = confirm_password
                db.session.commit()
                flash('Password updated', category='success')
                return redirect(url_for('profile_page', customer_id=customer_id))
            flash('New passwords do not match', category='danger')
        else:
            flash('Current password is incorrect', category='danger')
    if current_user.id == customer_id:
        return render_template('change-password.html', form=form)
    return render_template(ACCESS_DENIED_HTML)


@app.route('/create_product', methods=['GET', 'POST'])
@login_required
def create_product():
    if current_user.email == ADMIN_EMAIL:
        form = ShopItemsForm()
        if form.validate_on_submit():
            product_name = form.product_name.data
            price = form.price.data
            quantity = form.quantity.data
            description = form.description.data
            file = form.product_image.data
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
            db.session.add(new_product)
            db.session.commit()
            flash(f'{product_name} Added Successfully', category='success')
            return render_template('create-product.html', form=form)
        if form.errors != {}:  # If there are errors from the validations
            for err_msg in form.errors.values():
                flash(f'There was an error with adding a product: {err_msg}', category='danger')
        return render_template('create-product.html', form=form)
    return render_template(ACCESS_DENIED_HTML)


@app.route('/view-shop-items', methods=['GET', 'POST'])
@login_required
def shop_items():
    if current_user.email == ADMIN_EMAIL:
        items = Product.query.order_by(Product.date_added).all()
        return render_template('shop_items.html', items=items)
    return render_template(ACCESS_DENIED_HTML)


@app.route('/update-item/<int:product_id>', methods=['GET', 'POST'])
@login_required
def update_item(product_id):
    if current_user.email == ADMIN_EMAIL:
        form = ShopItemsForm()
        item_to_update = Product.query.get(product_id)
        form.product_name.render_kw = {'placeholder': item_to_update.name}
        form.price.render_kw = {'placeholder': item_to_update.price}
        form.quantity.render_kw = {'placeholder': item_to_update.quantity}
        form.description.render_kw = {'placeholder': item_to_update.description}
        if form.validate_on_submit():
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
            db.session.commit()
            flash(f'{product_name} Updated Successfully', category='success')
            return redirect(url_for('shop_items'))
        if form.errors != {}:  # If there are errors from the validations
            for err_msg in form.errors.values():
                flash(f'There was an error with updating a product: {err_msg}', category='danger')
        return render_template('update_item.html', form=form)
    return render_template(ACCESS_DENIED_HTML)


@app.route('/delete-item/<int:product_id>', methods=['GET', 'DELETE'])
@login_required
def delete_item(product_id):
    if current_user.email == ADMIN_EMAIL:
        item_to_delete = Product.query.get(product_id)
        db.session.delete(item_to_delete)
        db.session.commit()
        flash('Item Deleted Successfully', category='success')
        return redirect(url_for('shop_items'))
    return render_template(ACCESS_DENIED_HTML)


@app.route('/add-to-cart/<int:product_id>', methods=['GET', 'POST'])
@login_required
def add_to_cart(product_id):
    item_to_add = Product.query.get(product_id)
    item_exists = Cart.query.filter_by(product_id=product_id, customer_id=current_user.id).first()
    if item_exists:
        item_exists.quantity += 1
        db.session.commit()
        flash('Item Added Successfully', category='success')
        return redirect(request.referrer)
    new_cart_item = Cart()
    new_cart_item.quantity = 1
    new_cart_item.product_id = item_to_add.id
    new_cart_item.customer_id = current_user.id
    db.session.add(new_cart_item)
    db.session.commit()
    flash(f'{new_cart_item.product.name} Added Successfully', category='success')
    return redirect(request.referrer)


@app.route('/increase-quantity', methods=['GET'])
@login_required
def increase_quantity():
    cart_id = request.args.get('cart_id')
    cart_item = Cart.query.get(cart_id)
    cart_item.quantity += 1
    db.session.commit()
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
    cart_id = request.args.get('cart_id')
    cart_item = Cart.query.get(cart_id)
    cart_item.quantity -= 1
    db.session.commit()
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
    cart_id = request.args.get('cart_id')
    cart_item = Cart.query.get(cart_id)
    db.session.delete(cart_item)
    db.session.commit()
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
    cart = Cart.query.filter_by(customer_id=current_user.id).all()
    amount = 0
    for item in cart:
        amount += item.product.price * item.quantity
    return render_template('cart.html', cart=cart, amount=amount)


@app.route('/place-order')
@login_required
def place_order():
    customer_cart = Cart.query.filter_by(customer_id=current_user.id)
    if customer_cart:
        try:
            total = 0
            for item in customer_cart:
                total += item.product.price * item.quantity
            service = APIService(token=API_TOKEN, publishable_key=API_PUBLISHABLE_KEY, test=True)
            create_order_response = service.collect.mpesa_stk_push(phone_number='25472000000',
                                                                   email=current_user.email,
                                                                   amount=total,
                                                                   narrative='Purchase',
                                                                   currency='GBP',
                                                                   api_ref='API Request')
            for item in customer_cart:
                new_order = Order()
                new_order.quantity = item.quantity
                new_order.price = item.product.price
                new_order.status = create_order_response['invoice']['state'].capitalize()
                new_order.payment_id = create_order_response['id']
                new_order.product_id = item.product_id
                new_order.customer_id = item.customer_id
                db.session.add(new_order)
                product = Product.query.get(item.product_id)
                if product.quantity - item.quantity >= 0:
                    product.quantity -= item.quantity
                    db.session.delete(item)
                    db.session.commit()
                else:
                    raise CustomException('Item is not available')
            flash('Order Placed Successfully', category='success')
            return redirect(url_for('my_orders'))
        except CustomException:
            flash('Order not placed', category='danger')
            return redirect(url_for('home_page'))


@app.route('/orders')
@login_required
def my_orders():
    orders = Order.query.filter_by(customer_id=current_user.id).all()
    return render_template('orders.html', orders=orders)


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form.get('search')
        items = Product.query.filter(Product.name.ilike(f'%{search_query}%')).all()
        return render_template('search.html', items=items,
                               cart=Cart.query.filter_by(customer_id=current_user.id).all()
                               if current_user.is_authenticated else [])

    return render_template('search.html')


@app.route('/view-orders')
@login_required
def order_view():
    if current_user.email == ADMIN_EMAIL:
        orders = Order.query.all()
        return render_template('view_orders.html', orders=orders)
    return render_template(ACCESS_DENIED_HTML)


@app.route('/update-order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def update_order(order_id):
    if current_user.email == ADMIN_EMAIL:
        form = OrderForm()

        order = Order.query.get(order_id)

        if form.validate_on_submit():
            status = form.order_status.data
            order.status = status

            db.session.commit()
            flash(f'Order {order_id} Updated successfully', category='success')
            return redirect(url_for('order_view'))
        flash(f'Order {order_id} not updated', category='danger')
        return render_template('order_update.html', form=form)
    return render_template(ACCESS_DENIED_HTML)


@app.route('/customers')
@login_required
def display_customers():
    if current_user.email == ADMIN_EMAIL:
        customers = Customer.query.all()
        return render_template('customers.html', customers=customers)
    return render_template(ACCESS_DENIED_HTML)


@app.route('/customers/<int:customer_id>', methods=['GET', 'DELETE'])
@login_required
def delete_customer(customer_id):
    if current_user.email == ADMIN_EMAIL:
        account_to_delete = Customer.query.get(customer_id)
        print(account_to_delete)
        db.session.delete(account_to_delete)
        db.session.commit()
        flash(
            f"The account with the email '{account_to_delete.email}' has been deleted",
            category='success')
        return redirect(url_for('display_customers'))
    return render_template(ACCESS_DENIED_HTML)
