from flask import blueprints
from api_gateway.views.home import home
from api_gateway.views.auth import auth
"""from .users import users
from .restaurants import restaurants
from .authority import authority
from .reservations import reservations
from .customer_reservations import customer_reservations"""

# blueprints = [home, auth, users, restaurants, reservations, authority, customer_reservations]
blueprints = [home, auth]