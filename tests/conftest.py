"""
Configuración de pytest para el proyecto Asistente de Ferias RAA.
Configura el pythonpath para importar la app desde la raíz del proyecto.
"""
import sys
from pathlib import Path

# Agregar la raíz del proyecto al pythonpath
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
