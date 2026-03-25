import os
import sys

# Agregamos la ruta de la carpeta actual y de erp_app para que Python no se pierda
base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, base_dir)
sys.path.insert(0, os.path.join(base_dir, 'erp_app'))

# Importamos la función que crea la aplicación
try:
    from erp_app.app import create_app
except ImportError:
    from app import create_app

app = create_app()

if __name__ == "__main__":
    # Render asigna un puerto dinámico (PORT). Si no existe, usamos el 5000.
    port = int(os.environ.get("PORT", 5000))
    
    # 0.0.0.0 es obligatorio para que Render pueda 'ver' tu app desde afuera
    app.run(host='0.0.0.0', port=port, debug=False)
