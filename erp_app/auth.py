from flask import session, redirect, url_for, request
from functools import wraps
from models import Usuario
import os

def usuario_requerido(f):
    """Decorador para requerir que el usuario esté autenticado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_requerido(f):
    """Decorador para requerir que el usuario sea admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login', next=request.url))
        
        usuario = Usuario.query.get(session['usuario_id'])
        if not usuario or not usuario.is_admin():
            return redirect(url_for('inicio'))
        
        return f(*args, **kwargs)
    return decorated_function

def get_usuario_actual():
    """Obtiene el usuario actual de la sesión"""
    if 'usuario_id' in session:
        return Usuario.query.get(session['usuario_id'])
    return None
