"""Init file for the application"""
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eCommerceWebsite.db'
app.config['SECRET_KEY'] = '18685102678fc92100c58b50'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


@app.errorhandler(404)
def page_not_found(error):
    """
    Renders the 404 page when attempting to access a page that does not exist
    :param error: The error code
    :return: 404 page
    """
    print(error)
    return render_template('404.html')


login_manager = LoginManager(app)
login_manager.login_view = 'login_page'
login_manager.login_message_category = 'info'
from main import routes
