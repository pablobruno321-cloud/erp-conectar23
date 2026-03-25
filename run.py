import os
import sys

# Mantenemos tus rutas originales para que no falle la importación
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'erp_app'))

# Esto es lo que tenías en la línea 13
from app import app

if __name__ == '__main__':
    # Detectar entorno
    is_production = os.getenv('FLASK_ENV') == 'production'

    if not is_production:
        # Desarrollo local
        app.run(debug=True, host='127.0.0.1', port=5000)
    else:
        # PRODUCCIÓN (RENDER): Usamos el puerto que nos asigne el servidor
        port = int(os.environ.get("PORT", 8000))
        # host='0.0.0.0' es fundamental
        app.run(debug=False, host='0.0.0.0', port=port)
