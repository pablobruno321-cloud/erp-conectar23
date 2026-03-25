import os
import sys
from erp_app import create_app

# Configuración de rutas para que encuentre la carpeta erp_app
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

app = create_app()

if __name__ == "__main__":
    # Render nos asigna un puerto dinámico, acá lo capturamos.
    # Si no hay puerto (en tu PC), usa el 5000 por defecto.
    port = int(os.environ.get("PORT", 5000))
    
    # host='0.0.0.0' es fundamental para que Render pueda ver la app.
    # debug=False para producción (más seguro y rápido).
    app.run(host='0.0.0.0', port=port, debug=False)
