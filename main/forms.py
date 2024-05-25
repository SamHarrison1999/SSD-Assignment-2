from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, IntegerField, FloatField, PasswordField, EmailField, SubmitField
from wtforms.fields.choices import SelectField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError

from main.models import Customer


class RegisterForm(FlaskForm):

    def validate_username(self, username_to_check):
        user = Customer.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError(
                f"Username '{self.username}' already exists! Please try a different username"
            )

    def validate_email(self, email_to_check):
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
    email = EmailField(label='Email Address:', validators=[Email(), DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label='Login')


class PurchaseItemForm(FlaskForm):
    submit = SubmitField(label='Purchase Item!')


class SellItemForm(FlaskForm):
    submit = SubmitField(label='Sell Item!')


class ChangePasswordForm(FlaskForm):
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
    product_name = StringField('Product Name', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    product_image = FileField('Product Image', validators=[FileRequired()])
    add_product = SubmitField(label='Add Product')
    update_product = SubmitField(label='Update Product')


class OrderForm(FlaskForm):
    order_status = SelectField('Order Status', choices=[
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Out for delivery', 'Out for delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled')
    ])
    update = SubmitField(label='Update Status')
