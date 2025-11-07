import os
import dotenv
import logging
from .logger import setup_logger 

# --- 0. CONFIGURACIÓN INICIAL Y CONSTANTES ---

# Obtiene la ruta absoluta del directorio donde se encuentra este archivo config.py
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Navega un nivel arriba para llegar a la raíz del proyecto (Ej: C:\...\Automation Exercise)
PROJECT_ROOT = os.path.dirname(CURRENT_DIR) 

# Constantes
AMBIENTE_POR_DEFECTO = "qa"
# Define aquí TODAS las variables de entorno que son CRÍTICAS para el funcionamiento del framework.
# Estas variables deben estar definidas en el .env del ambiente seleccionado (ej: qa.env, dev.env).
VARIABLES_ENTORNO_CRITICAS = [
    "BASE_URL", 
    "SIGNIN_URL", 
    "SIGNUP_URL", 
    # --- NUEVAS VARIABLES DE TRELLO ---
    "TRELLO_API_KEY",
    "TRELLO_API_TOKEN",
    "TRELLO_FAIL_LIST_ID",
    "TRELLO_QA_LIST_ID",
    "TRELLO_ONGOING_LIST_ID",
    "TRELLO_DONE_LIST_ID",
    "TRELLO_REPORTING_ENABLED",
    # --- NUEVAS VARIABLES DE JIRA ---
    "JIRA_URL",
    "JIRA_API_USER",
    "JIRA_API_TOKEN",
    "JIRA_PROJECT_KEY",
    "JIRA_ISSUE_TYPE",
    #"JIRA_SECURITY_LEVEL_ID",
    "JIRA_REPORTING_ENABLED"
] 

# --- 1. CONFIGURACIÓN DE AMBIENTES Y CARGA DE VARIABLES ---

DIRECTORIO_AMBIENTES = os.path.join(PROJECT_ROOT, "environments")

# Obtiene el nombre del ambiente. Si no se especifica (ENVIRONMENT), usa la constante por defecto ("qa").
AMBIENTE = os.getenv("ENVIRONMENT", AMBIENTE_POR_DEFECTO)

# Construye la ruta al archivo .env específico del ambiente (Ej: /environments/qa.env)
archivo_dotenv = os.path.join(DIRECTORIO_AMBIENTES, f"{AMBIENTE}.env")

# Carga las variables...
if os.path.exists(archivo_dotenv):
    dotenv.load_dotenv(archivo_dotenv)
else:
    pass # Se notifica al final, después de inicializar el logger


# --- 2. CONFIGURACIÓN DE URLS Y ASIGNACIÓN ---
# Las variables de entorno se obtienen del proceso, ya sea desde el .env cargado o desde variables del sistema.
BASE_URL = os.getenv("BASE_URL")
SIGNIN_URL = os.getenv("SIGNIN_URL")
SIGNUP_URL = os.getenv("SIGNUP_URL")
# --- 2.1 NUEVAS VARIABLES DE TRELLO ---
TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_API_TOKEN = os.getenv("TRELLO_API_TOKEN")
TRELLO_FAIL_LIST_ID = os.getenv("TRELLO_FAIL_LIST_ID")
TRELLO_QA_LIST_ID = os.getenv("TRELLO_QA_LIST_ID")
TRELLO_ONGOING_LIST_ID = os.getenv("TRELLO_ONGOING_LIST_ID")
TRELLO_DONE_LIST_ID = os.getenv("TRELLO_DONE_LIST_ID")
# Nueva variable: se convierte el valor de string a booleano. Por defecto, False si no existe.
TRELLO_REPORTING_ENABLED = os.getenv("TRELLO_REPORTING_ENABLED", 'False').lower() in ('true', '1', 't')
# --- 2.2 NUEVAS VARIABLES DE JIRA ---
JIRA_URL = os.getenv("JIRA_URL")
JIRA_API_USER = os.getenv("JIRA_API_USER")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")
JIRA_ISSUE_TYPE = os.getenv("JIRA_ISSUE_TYPE")
JIRA_SECURITY_LEVEL_ID = os.getenv("JIRA_SECURITY_LEVEL_ID")
# Nueva variable: se convierte el valor de string a booleano. Por defecto, False si no existe.
JIRA_REPORTING_ENABLED = os.getenv("JIRA_REPORTING_ENABLED", 'False').lower() in ('true', '1', 't')


# --- 3. RUTAS DE ALMACENAMIENTO DE EVIDENCIAS ---
# Todos los reportes se guardarán bajo 'PROJECT_ROOT/reports'
DIRECTORIO_BASE_EVIDENCIAS = os.path.join(PROJECT_ROOT, "reports")

# Subdirectorios para diferentes tipos de evidencia/archivos
VIDEO_DIR = os.path.join(DIRECTORIO_BASE_EVIDENCIAS, "video")           # Archivos .webm
TRACEVIEW_DIR = os.path.join(DIRECTORIO_BASE_EVIDENCIAS, "traceview") # Archivos .zip
SCREENSHOT_DIR = os.path.join(DIRECTORIO_BASE_EVIDENCIAS, "imagen")   # Archivos .png
LOGGER_DIR = os.path.join(DIRECTORIO_BASE_EVIDENCIAS, "log")          # Archivos .log

# Directorios para manejo de archivos del test
SOURCE_FILES_DIR_DATA_WRITE = os.path.join(PROJECT_ROOT, "tests", "files", "files_data_write")
SOURCE_FILES_DIR_DATA_SOURCE = os.path.join(PROJECT_ROOT, "tests", "files", "files_data_source")
SOURCE_FILES_DIR_UPLOAD = os.path.join(PROJECT_ROOT, "tests", "files", "files_upload")
SOURCE_FILES_DIR_DOWNLOAD = os.path.join(PROJECT_ROOT, "tests", "files", "files_download")


# --------------------------------------------------------------------------
# --- 4. INICIALIZACIÓN DEL LOGGER (CONFIGURACIÓN) ---

# Se crea el directorio de logs ANTES de llamar a setup_logger para asegurar que el archivo de log se pueda escribir.
try:
    os.makedirs(LOGGER_DIR, exist_ok=True)
except Exception as e:
    # Usamos print y raise aquí porque el logger aún no está totalmente inicializado.
    print(f"\nERROR FATAL (pre-logger): No se pudo crear el directorio de logs '{LOGGER_DIR}'.")
    raise EnvironmentError(f"\nFallo al configurar el directorio de logs: {e}")


# Inicializamos el logger pasándole la ruta. Nombre: 'config_setup'.
logger = setup_logger(
    name='config_setup', 
    console_level=logging.INFO, 
    file_level=logging.DEBUG,
    log_dir=LOGGER_DIR 
)
# --------------------------------------------------------------------------


# Notificaciones del paso 1 (Ahora que el logger está listo)
if os.path.exists(archivo_dotenv):
    logger.info(f"\nCargando variables de entorno para ambiente: '{AMBIENTE}' desde '{archivo_dotenv}'")
else:
    logger.warning(f"\nAdvertencia: Archivo de entorno '{archivo_dotenv}' NO encontrado. Usando variables de entorno del sistema (o valores vacíos).")


# --- 5. FUNCIÓN PARA ASEGURAR DIRECTORIOS (MEJORADA) ---

def asegurar_directorios_existan():
    """
    Crea los directorios necesarios si no existen.

    Si falla la creación de un directorio esencial (ej. por permisos o ruta inválida),
    lanza una excepción EnvironmentError para detener la ejecución de Pytest.
    """
    directorios_a_verificar = [
        VIDEO_DIR, 
        TRACEVIEW_DIR, 
        SCREENSHOT_DIR, 
        LOGGER_DIR,
        SOURCE_FILES_DIR_DATA_WRITE, 
        SOURCE_FILES_DIR_DATA_SOURCE,
        SOURCE_FILES_DIR_UPLOAD, 
        SOURCE_FILES_DIR_DOWNLOAD
    ]
    
    logger.info("\nVerificando y asegurando la existencia de directorios base...")

    for directorio in directorios_a_verificar:
        try:
            os.makedirs(directorio, exist_ok=True)
            logger.debug(f"\nDirectorio OK: {directorio}")
        except OSError as e:
            # === MEJORA 2: REGISTRO DETALLADO Y LANZAMIENTO CRÍTICO ===
            error_msg = (
                f"\nERROR CRÍTICO: Fallo al crear el directorio esencial '{directorio}'. "
                f"\nCausa probable: Permisos insuficientes o ruta inválida."
            )
            logger.critical(error_msg, exc_info=True) # Registra el traceback (permisos, espacio, etc.)
            raise EnvironmentError(error_msg) from e 

    logger.info("\nVerificación de directorios finalizada.")


# --- 6. FUNCIÓN DE VALIDACIÓN (OPTIMIZADA) ---

def validar_variables_entorno_criticas():
    """
    Valida que todas las variables de entorno críticas (definidas en VARIABLES_ENTORNO_CRITICAS)
    estén definidas y no estén vacías. Detiene la ejecución si alguna falta.
    """
    todas_cargadas = True
    variables_faltantes = []

    for var in VARIABLES_ENTORNO_CRITICAS:
        if not os.getenv(var) or not os.getenv(var).strip():
            # === MEJORA 1: MENSAJE CONCISO ===
            logger.critical(f"\nCRÍTICO: Variable '{var}' no definida o vacía. Ambiente: '{AMBIENTE}'.")
            todas_cargadas = False
            variables_faltantes.append(var)
    
    # Detención forzada si faltan variables críticas
    if not todas_cargadas:
        error_msg = (
            f"\nFallo en la configuración. Ejecución detenida. "
            f"\nVariables críticas FALTANTES en ambiente '{AMBIENTE}': {', '.join(variables_faltantes)}"
        )
        logger.critical(error_msg)
        raise EnvironmentError(error_msg)
    
    logger.info("\nTodas las variables de entorno críticas han sido validadas correctamente.")

    # Informar las variables cargadas (solo a nivel DEBUG para no saturar INFO)
    variables_a_debuggear = [
        ("BASE_URL", BASE_URL), 
        ("SIGNIN_URL", SIGNIN_URL),
        ("SIGNUP_URL", SIGNUP_URL), 
        # --- NUEVAS VARIABLES DE TRELLO ---
        ("TRELLO_API_KEY", "***********" if TRELLO_API_KEY else None),
        ("TRELLO_API_TOKEN", "***********" if TRELLO_API_TOKEN else None),
        ("TRELLO_FAIL_LIST_ID", TRELLO_FAIL_LIST_ID),
        ("TRELLO_QA_LIST_ID", TRELLO_QA_LIST_ID),
        ("TRELLO_ONGOING_LIST_ID", TRELLO_ONGOING_LIST_ID),
        ("TRELLO_DONE_LIST_ID", TRELLO_DONE_LIST_ID),
        ("TRELLO_REPORTING_ENABLED", TRELLO_REPORTING_ENABLED),
        # --- NUEVAS VARIABLES DE JIRA ---
        ("JIRA_URL", JIRA_URL),
        ("JIRA_API_USER", "***********" if JIRA_API_USER else None),
        ("JIRA_API_TOKEN", "***********" if JIRA_API_TOKEN else None),
        ("JIRA_PROJECT_KEY", JIRA_PROJECT_KEY),
        ("JIRA_ISSUE_TYPE", JIRA_ISSUE_TYPE),
        ("JIRA_SECURITY_LEVEL_ID", JIRA_SECURITY_LEVEL_ID),
        ("JIRA_REPORTING_ENABLED", JIRA_REPORTING_ENABLED),
    ]
    for var_name, var_value in variables_a_debuggear:
        logger.debug(f"\nConfiguración final: {var_name} = '{var_value}'")


# --- 7. EJECUCIÓN FINAL AL IMPORTAR EL MÓDULO ---

validar_variables_entorno_criticas() 
asegurar_directorios_existan()

# --- 8. UTILIDAD PARA OBTENER CONFIGURACIÓN (PARA MÓDULOS EXTERNOS) ---

FRAMEWORK_LOGGER = logger

def get_setting(key: str):
    """
    Función que permite a otros módulos obtener valores de configuración
    usando el nombre de la variable de entorno.
    """
    # Usamos os.getenv para flexibilidad, pero podríamos usar un diccionario interno 
    # si solo quisiéramos exponer las variables validadas.
    return os.getenv(key)