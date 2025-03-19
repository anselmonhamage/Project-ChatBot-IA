from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def auth_role(role):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            roles = role if isinstance(role, list) else [role]
            if all(not current_user.has_role(r) for r in roles):
                flash(f"Não tem a permissão de {','.join(roles)}", "danger")
                return redirect(url_for('index'))
            return fn(*args, **kwargs)

        return decorator

    return wrapper
