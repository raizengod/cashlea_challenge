import logging
from datetime import datetime
import os # Nueva
import glob # Nueva
from utils import config 
from utils.config import FRAMEWORK_LOGGER

# Por ahora, usamos un logger simple para evitar dependencia circular.
logger = logging.getLogger('test_helpers')

# Usamos el logger del framework para registrar eventos internos de la utilidad
logger = FRAMEWORK_LOGGER

# Por ahora, usamos un logger simple para evitar dependencia circular.
# En un entorno real, aseguraríamos que setup_logger se haya ejecutado.
try:
    from utils.logger import setup_logger
    logger = setup_logger(name='test_helpers', console_level=logging.INFO, file_level=logging.DEBUG, log_dir=config.LOGGER_DIR)
except:
    logger = logging.getLogger('test_helpers')

# --- FUNCIONES AUXILIARES MOVIDAS DE conftest.py ---

def _buscar_evidencias_por_nombre_test(test_name: str) -> list[str]:
    """
    Busca los archivos de evidencia (captura de pantalla de teardown, video, traceview)
    asociados al test fallido utilizando el nombre completo del test (incluyendo la parametrización).

    Args:
        test_name (str): El nombre completo del test de Pytest (ej: 'test_x[chromium-1920x1080]').

    Returns:
        list[str]: Una lista de rutas absolutas de los archivos de evidencia encontrados.
    """
    # [LOGGER AÑADIDO]
    logger.debug(f"[UTIL] Buscando evidencias para el test: {test_name}")
    
    evidencias_encontradas = []
    
    # 1. Preparar el nombre seguro para la búsqueda (CRÍTICO)
    # El nombre se limpia para coincidir con cómo se nombran los archivos en el teardown 
    # (reemplazando caracteres como '[', ']' por '_').
    safe_test_name = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in test_name)
    
    # --- 1. Buscar Captura de Pantalla (TEARDOWN_FINAL_STATE) ---
    # Busca la captura de pantalla final (la última que se tomó en el teardown del fixture).
    screenshot_pattern = f"TEARDOWN_FINAL_STATE_{safe_test_name}*.png" 
    screenshot_search_path = os.path.join(config.SCREENSHOT_DIR, screenshot_pattern)
    
    screenshots = glob.glob(screenshot_search_path)
    
    if screenshots:
        # Buena práctica: usar 'max' con os.path.getmtime para obtener el archivo MÁS RECIENTE
        latest_screenshot = max(screenshots, key=os.path.getmtime)
        evidencias_encontradas.append(latest_screenshot)
        logger.debug(f"Evidencia encontrada (Screenshot): {latest_screenshot}")
    else:
        logger.warning(f"⚠️ Advertencia: No se encontró la captura de pantalla para el patrón: {screenshot_pattern}")
    
    # --- 2. Buscar Video ---
    video_pattern = f"{safe_test_name}*.webm"
    video_search_path = os.path.join(config.VIDEO_DIR, video_pattern)
    list_of_videos = glob.glob(video_search_path)
    
    if list_of_videos:
        # Tomar el video MÁS RECIENTE que coincida con el patrón de nombre
        latest_video = max(list_of_videos, key=os.path.getmtime)
        evidencias_encontradas.append(latest_video)
        logger.debug(f"Evidencia encontrada (Video): {latest_video}")
    else:
        logger.warning(f"⚠️ Advertencia: No se encontró el video para el patrón: {video_pattern}")

    # --- 3. Buscar Traceview ---
    # El patrón corregido ahora busca el nombre del test dentro del nombre del archivo Traceview.
    # Patrón: traceview_*_{safe_test_name}*.zip (la lógica del glob lo hace flexible)
    trace_pattern = f"*{safe_test_name}*.zip" 
    trace_search_path = os.path.join(config.TRACEVIEW_DIR, trace_pattern)
    list_of_traces = glob.glob(trace_search_path)
    
    if list_of_traces:
        # Tomar el traceview MÁS RECIENTE
        latest_trace = max(list_of_traces, key=os.path.getmtime)
        evidencias_encontradas.append(latest_trace)
        logger.debug(f"Evidencia encontrada (Traceview): {latest_trace}")
    else:
        # La advertencia anterior es CRÍTICA, ya que indica un problema de nomenclatura o ruta.
        logger.warning(f"⚠️ Advertencia: No se encontró el Traceview para el patrón: {trace_pattern}")

    # [LOGGER AÑADIDO]
    logger.debug(f"[UTIL] Búsqueda de evidencias finalizada. Total encontrados: {len(evidencias_encontradas)}")
    return evidencias_encontradas

def _obtener_video_evidencia(test_name: str) -> str | None:
    """
    Busca la ruta absoluta del archivo de video (.webm) asociado al test
    utilizando el patrón de nombre de archivo.

    Args:
        test_name (str): El nombre completo del test de Pytest (ej: 'test_x[chromium-1920x1080]').

    Returns:
        str | None: La ruta absoluta del archivo de video más reciente o None si no se encuentra.
    """
    logger.debug(f"\n[UTIL] Intentando obtener ruta de video para el test de éxito: {test_name}")
    
    # 1. Preparar el nombre seguro para la búsqueda (CRÍTICO)
    safe_test_name = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in test_name)
    
    # 2. Buscar Video
    video_pattern = f"{safe_test_name}*.webm"
    video_search_path = os.path.join(config.VIDEO_DIR, video_pattern)
    list_of_videos = glob.glob(video_search_path)
    
    if list_of_videos:
        # Tomar el video MÁS RECIENTE que coincida con el patrón de nombre
        latest_video = max(list_of_videos, key=os.path.getmtime)
        logger.debug(f"\nEvidencia de video encontrada: {latest_video}")
        return latest_video
    else:
        logger.warning(f"\n⚠️ Advertencia: No se encontró el video para el test exitoso con el patrón: {video_pattern}")
        return None

def _registrar_paso_ejecutado(paso_nombre: str, item):
    """
    Función auxiliar para registrar el nombre de un paso en el fixture 'test_steps'.

    Esta función debe ser llamada desde las clases de acciones/páginas. Accede directamente 
    al fixture activo utilizando el objeto de solicitud ('item') del test actual.

    Args:
        paso_nombre (str): La descripción legible del paso ejecutado.
        item (pytest.Function): El objeto Function de Pytest, que contiene el objeto Request.
    """
    logger.debug(f"\n[UTIL] Intentando registrar paso: {paso_nombre}")
    
    try:
        # Accede al fixture 'test_steps' a través del request asociado al item de Pytest.
        # Es el método estándar para acceder a fixtures desde utilidades externas.
        # Se asume que 'item' aquí es el objeto 'request.node' o similar, y que tiene
        # el atributo '_request' para acceder a la funcionalidad de fixture.
        test_steps_list = item._request.getfixturevalue('test_steps')
        
        if isinstance(test_steps_list, list):
            # --- CÁLCULO DEL NÚMERO SECUENCIAL (Añadido desde el otro helper) ---
            step_number = len(test_steps_list) + 1

            # Formatea el paso con timestamp para el reporte.
            timestamp = datetime.now().strftime("%H:%M:%S")
            # --- INCLUSIÓN DEL NÚMERO EN EL FORMATO ---
            test_steps_list.append(f"[{step_number}.-] [{timestamp}] -> {paso_nombre}")

            # Log de depuración
            logger.debug(f"\nPaso registrado #{step_number}: {paso_nombre}")

    except Exception as e:
        # Se usa debug para silenciar errores si el test no usa 'test_steps' o si el 
        # fixture ya ha sido limpiado (aunque la corrección del generador minimiza esto).
        logger.debug(f"\nNo se pudo registrar el paso '{paso_nombre}' en el fixture 'test_steps'. Detalle: {e}")
        pass