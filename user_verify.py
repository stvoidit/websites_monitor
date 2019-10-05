from flask import flash, session, redirect, url_for, abort
from functools import wraps
from app import app


def login_required(roles=[], deps=[], strictly=False):
    def wrapper(func):
        @wraps(func)
        def roles_required(*args, **kwargs):
            with app.app_context():
                islogged = session.get('logged_in', False)
                check = [
                    session.get('role', None) in roles,
                    session.get("department", None) in deps
                ]
                roles.append('admin') if roles or deps else None
                if not roles and not deps and islogged:
                    """ Если аргументы пустые, но авторизован - пустить """
                    return func(*args, **kwargs)
                if islogged and strictly and all(check):
                    """ Строгая проверка """
                    return func(*args, **kwargs)
                elif islogged and not strictly and any(check):
                    """ НЕ строгая проверка strictly=False """
                    return func(*args, **kwargs)
                elif islogged:
                    """ Если авторизованный пользователь не имеет доступа """
                    return abort(401)
                else:
                    """ Если нет доступа и не авторизован """
                    return redirect(url_for('login'))
        return roles_required
    return wrapper
