# File: /topsis-streamlit/topsis-streamlit/routes/__init__.py

from flask import Blueprint

# Initialize the routes blueprint
routes_bp = Blueprint('routes', __name__)

# Import routes to register them with the blueprint
from .auth import *
from .topsis import *