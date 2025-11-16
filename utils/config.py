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
    "LOGIN_URL", 
    "REGISTER_URL",
    "WEBINPUT_URL",
    "DYNAMICTABLE_URL",
    "USERDASHBOARD_URL",
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
LOGIN_URL = os.getenv("LOGIN_URL")
REGISTER_URL = os.getenv("REGISTER_URL")
WEBINPUT_URL = os.getenv("WEBINPUT_URL")
DYNAMICTABLE_URL = os.getenv("DYNAMICTABLE_URL")
USERDASHBOARD_URL = os.getenv("USERDASHBOARD_URL")
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
DIRECTORIO_BASE_REPORTS = os.path.join(PROJECT_ROOT, "reports") 

# Subdirectorios BASE para diferentes tipos de evidencia/archivos.
# El subdirectorio final para cada test se agregará en conftest.py
VIDEO_BASE_DIR = os.path.join(DIRECTORIO_BASE_REPORTS, "video") # Archivos .webm
TRACEVIEW_BASE_DIR = os.path.join(DIRECTORIO_BASE_REPORTS, "traceview") # Archivos .zip
SCREENSHOT_BASE_DIR = os.path.join(DIRECTORIO_BASE_REPORTS, "imagen") # Archivos .png
LOGGER_BASE_DIR = os.path.join(DIRECTORIO_BASE_REPORTS, "logs") # Archivos .log (cambio de 'log' a 'logs')

# Directorios para manejo de archivos del test
SOURCE_FILES_DIR_DATA_WRITE = os.path.join(PROJECT_ROOT, "tests", "files", "files_data_write")
SOURCE_FILES_DIR_DATA_SOURCE = os.path.join(PROJECT_ROOT, "tests", "files", "files_data_source")
SOURCE_FILES_DIR_UPLOAD = os.path.join(PROJECT_ROOT, "tests", "files", "files_upload")
SOURCE_FILES_DIR_DOWNLOAD = os.path.join(PROJECT_ROOT, "tests", "files", "files_download")

# --- 4. INICIALIZACIÓN DEL LOGGER (CONFIGURACIÓN) ---

# Se inicializa un logger global para uso en config.py, no específico de un test.
try:
    # Creamos SOLO el directorio BASE de logs para el log principal del framework.
    os.makedirs(LOGGER_BASE_DIR, exist_ok=True)
except Exception as e:
    # Usamos print y raise aquí porque el logger aún no está totalmente inicializado.
    print(f"\nCRÍTICO: No se pudo crear el directorio base de logs '{LOGGER_BASE_DIR}'. Detalles: {e}")
    raise


# Inicializar logger con el directorio base
logger = setup_logger(
    name='Configuration', 
    console_level=logging.INFO, 
    file_level=logging.DEBUG, 
    log_dir=LOGGER_BASE_DIR # Pasamos el directorio base
) 
logger.info(f"\nLogger 'Configuration' inicializado en: {LOGGER_BASE_DIR}")

# --- 5. FUNCIONES AUXILIARES DE VALIDACIÓN Y SETUP ---

def validar_variables_entorno_criticas():
    """
    Verifica que las variables de entorno críticas estén cargadas. Detiene la ejecución si alguna falta.
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
            f"\nVariables faltantes: {', '.join(variables_faltantes)}. "
            f"\nAsegure que el archivo '{archivo_dotenv}' exista y esté completo."
        )
        logger.error(error_msg)
        raise EnvironmentError(error_msg)
    else:
        logger.info("\nVALIDACIÓN: Todas las variables de entorno críticas están cargadas.")

def asegurar_directorios_base():
    """
    Asegura que los directorios base de evidencia y auxiliares existan. 
    Los directorios específicos de cada test se crearán en conftest.py.
    """
    directorios_a_crear = [
        VIDEO_BASE_DIR,
        TRACEVIEW_BASE_DIR,
        SCREENSHOT_BASE_DIR,
        LOGGER_BASE_DIR,
        DIRECTORIO_AMBIENTES,
        SOURCE_FILES_DIR_DATA_WRITE,
        SOURCE_FILES_DIR_DATA_SOURCE,
        SOURCE_FILES_DIR_UPLOAD,
        SOURCE_FILES_DIR_DOWNLOAD,
    ]

    for d in directorios_a_crear:
        try:
            os.makedirs(d, exist_ok=True)
            logger.debug(f"\nDirectorio asegurado: {d}")
        except Exception as e:
            logger.error(f"\nCRÍTICO: No se pudo crear el directorio '{d}'. Detalles: {e}")
            raise


# --- 6. DEBUG Y REGISTRO DE CONFIGURACIÓN ---

def registrar_configuracion_final():
    """
    Registra las configuraciones finales para debug, ocultando tokens sensibles.
    """
    # Lista de variables y sus valores (ocultando tokens)
    variables_a_debuggear = [
        ("AMBIENTE", AMBIENTE),
        # URLs
        ("BASE_URL", BASE_URL),
        ("LOGIN_URL", LOGIN_URL),
        ("REGISTER_URL", REGISTER_URL),
        ("WEBINPUT_URL", WEBINPUT_URL),
        ("DYNAMICTABLE_URL", DYNAMICTABLE_URL),
        ("USERDASHBOARD_URL", USERDASHBOARD_URL),
        # Rutas Base de Evidencias
        ("VIDEO_BASE_DIR", VIDEO_BASE_DIR),
        ("TRACEVIEW_BASE_DIR", TRACEVIEW_BASE_DIR),
        ("SCREENSHOT_BASE_DIR", SCREENSHOT_BASE_DIR),
        ("LOGGER_BASE_DIR", LOGGER_BASE_DIR),
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
asegurar_directorios_base() 
registrar_configuracion_final()

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