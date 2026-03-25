#!/usr/bin/env python
"""
Script para ejecutar el ERP
Úsalo así: python run.py
"""

import os
import sys

# Agregar la carpeta erp_app al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'erp_app'))

# Importar y ejecutar la app
from app import app

if __name__ == '__main__':
    # Detectar el entorno
    is_production = os.getenv('FLASK_ENV') == 'production'
    
    if not is_production:
        # Desarrollo local
        print("=" * 60)
        print("ERP - Sistema de Gestión Empresarial")
        print("=" * 60)
        print("\nLa aplicación está iniciándose...")
        print("Abre tu navegador en: http://localhost:5000")
        print("\nPresiona Ctrl+C para detener la aplicación\n")
        
        app.run(debug=True, host='127.0.0.1', port=5000)
    else:
        # Producción - no correr aquí, usar gunicorn
        print("Ejecutar en producción con: gunicorn --workers 3 --bind 0.0.0.0:8000 run:app")
        app.run(debug=False, host='0.0.0.0', port=8000)

