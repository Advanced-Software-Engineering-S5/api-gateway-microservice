import functools
from api_gateway.classes.user import User
from werkzeug.local import LocalProxy
from flask_jwt_extended import jwt_required, JWTManager, current_user, jwt_optional, get_jwt_identity, verify_jwt_in_request_optional
from flask import redirect, url_for, make_response, request

jwt_manager = JWTManager()
currently_logged_in = {}

current_user = LocalProxy(lambda: _get_jwt_user())

class AnonymousUser():
    pass


@jwt_optional
def _get_jwt_user():
    usr = currently_logged_in.get(str(get_jwt_identity()))
    return (usr if isinstance(usr, User) else None)


@jwt_manager.unauthorized_loader
def unauthorized(error_description):
    # TODO: return stuff
    return "Unauthorized " + error_description, 401


@jwt_manager.user_loader_callback_loader
def loader(user_id):
    if not currently_logged_in.get(str(user_id)):
        user = User.get(id=user_id)
        if user:
            user.is_authenticated = True
        currently_logged_in[str(user_id)] = user or AnonymousUser()
    return currently_logged_in.get(str(user_id))


@jwt_manager.expired_token_loader
def expired_token_callback():
    # Reset the cookies
    response = make_response()
    response.set_cookie('gooutsafe_jwt_token', "", expires=0)
    response.set_cookie("csrf_access_token", "", expires=0)
    response.status_code = 301
    response.location = url_for("auth.login")
    return response


# flask_jwt_extended fai cacare
def user_loader_ctx_processor():
    # Pass the JWT current_user as current_user like flask-login does
    return dict(current_user=current_user)


def admin_required(func):
    @functools.wraps(func)
    @jwt_required
    def _admin_required(*args, **kw):
        admin = current_user and current_user.is_admin
        if not admin:
            return unauthorized("You are not an health administrator")
        return func(*args, **kw)

    return _admin_required


def operator_required(func):
    @functools.wraps(func)
    @jwt_required
    def _operator_required(*args, **kw):
        if not current_user or not hasattr(current_user, "restaurant_id") or current_user.restaurant_id is None:
            return unauthorized("You are not an operator")

        return func(*args, **kw)

    return _operator_required


login_required = jwt_required
