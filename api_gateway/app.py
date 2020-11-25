# from database import Restaurant
#import connexion, logging
import logging
from api_gateway.auth import jwt_manager, user_loader_ctx_processor
from flask import Flask
from .views import blueprints

db_session = None

logging.basicConfig(level=logging.INFO)

def create_app():
    # db_session = database.init_db('sqlite:///restaurant.db')
    app = Flask(__name__)
    # app.add_api('swagger.yml')
    # app = app.app

    jwt_manager.init_app(app)
    app.context_processor(user_loader_ctx_processor)
    app.config['WTF_CSRF_SECRET_KEY'] = 'A SECRET KEY'
    app.config['JWT_SECRET_KEY'] = 'secret_key_bella_e_nascosta'
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_ACCESS_COOKIE_NAME'] = 'gooutsafe_jwt_token'
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    app.config['JWT_CSRF_IN_COOKIES'] = False
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
    app.secret_key = b'a#very#fantastic#secretkey'
    

    for bp in blueprints:
        app.register_blueprint(bp)
        bp.app = app

    return app


# @application.teardown_appcontext
# def shutdown_session(exception=None):
#     db_session.remove()

if __name__ == '__main__':
    app = create_app()
    app.run()