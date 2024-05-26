"""Class for tables in the database"""

import datetime
from flask_login import UserMixin
from main import db, login_manager
from main import bcrypt


@login_manager.user_loader
def load_user(user_id):
    """
    Function for logging in
    :param user_id: The user id
    :return: The user
    """
    return Customer.query.get(int(user_id))


class Customer(db.Model, UserMixin):
    """
    Class for the customer table
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(length=60), nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.datetime.now(datetime.UTC))
    cart_items = db.relationship('Cart', backref=db.backref('customer', lazy=True))
    orders = db.relationship('Order', backref=db.backref('customer', lazy=True))

    @property
    def password(self):
        """
        Function to prevent passwords from being read
        :raises: AttributeError: if an attempt is made to read the password attribute.
        :return:
        """
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password):
        """
        Function for converting a password to a hashed password and storing it in the database
        :param password: The plain text password
        :return:
        """
        # Applying hashing algorithm to the password
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        """
        Function for checking the password entered is correct
        :param password: The entered password
        :return: Boolean indicating if the entered password is correct
        """
        # Verify the user's password
        return bcrypt.check_password_hash(self.password_hash, password)

    def __str__(self):
        """
        Returns the id of the user as a string
        :return: The id of the user
        """
        return f'{self.id}'


class Product(db.Model):
    """
    Class for the product table
    """
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(1024), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    product_image = db.Column(db.String(1000), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.datetime.now(datetime.UTC))
    carts = db.relationship('Cart', backref=db.backref('product', lazy=True))
    orders = db.relationship('Order', backref=db.backref('product', lazy=True))


class Cart(db.Model):
    """
    Class for the cart table
    """
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)


class Order(db.Model):
    """
    Class for the order table
    """
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(100), nullable=False)
    payment_id = db.Column(db.String(1000), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
