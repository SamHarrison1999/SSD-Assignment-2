"""Init file for the application"""
# Import statements
import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from dotenv import load_dotenv

# Configuration for the app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eCommerceWebsite.db'
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
# Load environment variables from the .env file
load_dotenv()


@app.errorhandler(404)
def page_not_found(error):
    """
    Renders the 404 page when attempting to access a page that does not exist
    :param error: The error code
    :return: 404 page
    """
    print(error)
    # Displays the 404 error page to prevent information leakage
    return render_template('404.html')


# Login manager for the app
login_manager = LoginManager(app)
login_manager.login_view = 'login_page'
login_manager.login_message_category = 'info'
# Import routes
from main import routes
