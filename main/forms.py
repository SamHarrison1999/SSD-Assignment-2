"""File containing forms used in the application"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import (StringField,
                     IntegerField,
                     FloatField,
                     PasswordField,
                     EmailField,
                     SubmitField)
from wtforms.fields.choices import SelectField
from wtforms.validators import (Length,
                                EqualTo,
                                Email,
                                DataRequired,
                                ValidationError)

from main.models import Customer


class RegisterForm(FlaskForm):
    """
    Form used to sign up new users
    """

    def validate_username(self, username_to_check):
        """
        Function to check if the username is available
        :param username_to_check: The user's username
        :return:
        """
        user = Customer.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError(
                f"Username '{self.username}' already exists! Please try a different username"
            )

    def validate_email(self, email_to_check):
        """
        Function to check if the email is available
        :param email_to_check: The users email address
        :return:
        """
        email = (Customer.
                 query.
                 filter_by(email=email_to_check.data).first())
        if email:
            raise ValidationError(
                f"Email '{self.email}' already exists! Please try a different email"
            )

    username = StringField(label='User Name:', validators=[Length(min=2, max=30), DataRequired()])
    email = EmailField(label='Email Address:', validators=[Email(), DataRequired()])
    password = PasswordField(label='Password', validators=[Length(min=6), DataRequired()])
    confirm_password = PasswordField(
        label='Confirm Password:',
        validators=[EqualTo('password'), DataRequired()])
    submit = SubmitField(label='Create Account')


class LoginForm(FlaskForm):
    """
    Form used to sign in to your account
    """
    email = EmailField(label='Email Address:', validators=[Email(), DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label='Login')


class ChangePasswordForm(FlaskForm):
    """
    Form used by the user to change their password
    """
    current_password = PasswordField(
        label='Current Password',
        validators=[Length(min=6), DataRequired()])
    new_password = PasswordField(
        label='New Password',
        validators=[Length(min=6), DataRequired()])
    confirm_password = PasswordField(
        label='Confirm Password',
        validators=[Length(min=6), DataRequired()])
    submit = SubmitField(label='Update Password')


class ShopItemsForm(FlaskForm):
    """
    Form used to add items to the website
    """
    product_name = StringField('Product Name', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    product_image = FileField('Product Image', validators=[FileRequired()])
    add_product = SubmitField(label='Add Product')
    update_product = SubmitField(label='Update Product')


class OrderForm(FlaskForm):
    """
    Form used to place an order
    """
    order_status = SelectField('Order Status', choices=[
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Out for delivery', 'Out for delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled')
    ])
    update = SubmitField(label='Update Status')
