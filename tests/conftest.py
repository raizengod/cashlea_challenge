# nombra el archivo: Ve a la ubicación de tu archivo y colcoar el nombre a conftest.py
# La convención de conftest.py le indica a Pytest que este archivo contiene fixtures que deben estar disponibles 
# para los tests en ese directorio y sus subdirectorios.
import re
import pytest
import time
import datetime
import logging
from playwright.sync_api import Page, expect, Playwright, sync_playwright
from datetime import datetime
import os
from typing import Generator, List
from utils import config
from pages.base_page import BasePage
import allure
from utils.logger import setup_logger
from api_clients.trello_client import TrelloClient
import inspect
from utils.test_helpers import _registrar_paso_ejecutado, _buscar_evidencias_por_nombre_test, _obtener_video_evidencia
from utils.report_handlers import _handle_trello_reporting, _handle_jira_reporting

# Inicializar el logger con la configuración definida en config.py
# El logger se usará a nivel de módulo
logger = setup_logger(name='conftest', console_level=logging.INFO, file_level=logging.DEBUG, log_dir=config.LOGGER_DIR)

# Función para generar IDs legibles
def generar_ids_browser(param):
    """
    Genera un ID descriptivo para cada combinación de navegador y dispositivo.
    """
    browser = param['browser']
    device = param['device']
    resolution = param['resolution']

    if device:
        return f"{browser}-{device}"
    else:
        return f"{browser}-{resolution['width']}x{resolution['height']}"

@pytest.fixture(
    scope="function",
    params=[
            # Resoluciones de escritorio
            {"browser": "chromium", "resolution": {"width": 1920, "height": 1080}, "device": None},
            {"browser": "firefox", "resolution": {"width": 1920, "height": 1080}, "device": None},
            {"browser": "webkit", "resolution": {"width": 1920, "height": 1080}, "device": None},
            # Emulación de dispositivos móviles
            {"browser": "chromium", "device": "iPhone 12", "resolution": None},
            {"browser": "webkit", "device": "Pixel 5", "resolution": None},
            {"browser": "webkit", "device": "iPhone 12", "resolution": None}
    ],
    ids=generar_ids_browser # <--- Usar la función para generar IDs
)
def playwright_page(playwright: Playwright, request) -> Generator[Page, None, None]:
    """
    Fixture base para configurar el navegador, contexto y página de Playwright con configuraciones comunes.
    Maneja el lanzamiento del navegador, la creación del contexto (con grabación de video y emulación de dispositivos),
    el rastreo (tracing) y la navegación de la página a una URL específica. También renombra el archivo de video al finalizar.
    """
    param = request.param
    browser_type = param["browser"]
    resolution = param["resolution"]
    device_name = param["device"]

    browser_instance = None
    context = None
    page = None
    
    logger.info(f"\nIniciando fixture para {browser_type} / Dispositivo: {device_name if device_name else f'{resolution['width']}x{resolution['height']}'}")

    try:
        # --- 1. Lanzamiento del Navegador ---
        logger.debug(f"\nLanzando navegador: {browser_type}")
        if browser_type == "chromium":
            browser_instance = playwright.chromium.launch(headless=True, slow_mo=500)
        elif browser_type == "firefox":
            browser_instance = playwright.firefox.launch(headless=True, slow_mo=500)
        elif browser_type == "webkit":
            browser_instance = playwright.webkit.launch(headless=True, slow_mo=500)
        else:
            # Capturar tipo de navegador no compatible
            raise ValueError(f"\nEl tipo de navegador '{browser_type}' no es compatible.")

        # --- 2. Configuración del Contexto ---
        context_options = {
            "record_video_dir": config.VIDEO_DIR,
            "record_video_size": {"width": 1920, "height": 1080}
        }
        
        logger.debug("\nCreando contexto de Playwright...")
        if device_name:
            device = playwright.devices[device_name]
            context = browser_instance.new_context(**device, **context_options)
            logger.debug(f"\nContexto creado con emulación de dispositivo: {device_name}")
        elif resolution:
            context = browser_instance.new_context(viewport=resolution, **context_options)
            logger.debug(f"\nContexto creado con resolución: {resolution['width']}x{resolution['height']}")
        else:
            context = browser_instance.new_context(**context_options)
            logger.debug("\nContexto creado con opciones por defecto.")

        # --- 3. Creación de la Página ---
        page = context.new_page()

        # --- 4. Inicio de Tracing ---
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 🟢 CORRECCIÓN CLAVE: Obtener el nombre limpio del test para incluirlo en el nombre del trace
        # Esto asegura que el archivo Traceview sea único y que la búsqueda pueda encontrarlo
        test_name_with_params = request.node.name 
        safe_test_name = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in test_name_with_params)

        # Ahora el nombre del archivo incluirá el nombre del test (safe_test_name)
        # Esto alinea el nombre con el patrón de búsqueda existente en _buscar_evidencias_por_nombre_test
        trace_file_name = f"traceview_{current_time}_{safe_test_name}.zip"
        trace_path = os.path.join(config.TRACEVIEW_DIR, trace_file_name)

        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        logger.debug(f"\nTracing iniciado. El archivo se guardará en: {trace_path}")

        yield page # Ejecutar la prueba

    except ValueError as ve:
        # Capturar la excepción que lanzamos nosotros si el navegador no es soportado
        logger.error(f"\nError de configuración (Valor no válido): {ve}")
        pytest.skip(f"\nPrueba saltada debido a error en la configuración: {ve}") # Se puede optar por saltar la prueba
    except Exception as e:
        # Capturar cualquier otro error inesperado durante el setup (ej. error de Playwright al lanzar)
        logger.error(f"\nError inesperado durante el SETUP del fixture playwright_page: {e}", exc_info=True)
        # Re-lanzar para que Pytest marque el test como 'error'
        raise
    
    finally:
        # --- 5. Tareas de Cierre (Teardown) ---
        logger.info("\nIniciando Teardown del fixture playwright_page...")

        # Captura de pantalla de estado final para análisis de fallos
        if page:
            try:
                # Se utiliza el estatus del resultado del test (Pytest-specific) 
                # para determinar si el test falló (opcional, pero buena práctica).
                # Para un análisis más simple, simplemente capturamos el estado final.
                # Nota: request.node.name obtiene el nombre del test que usó la fixture.
                test_name = request.node.name
                # Limpiar el nombre del test para usarlo en el nombre del archivo (sustituye caracteres especiales por '_')
                safe_test_name = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in test_name)
                
                screenshot_name = f"TEARDOWN_FINAL_STATE_{safe_test_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                screenshot_path = os.path.join(config.SCREENSHOT_DIR, screenshot_name)

                # Tomar la captura de pantalla antes de cerrar cualquier recurso.
                page.screenshot(path=screenshot_path, full_page=True)
                logger.info(f"\n📸 Captura de pantalla de estado final guardada en: {screenshot_path}")

            except Exception as e:
                # Si falla la captura de pantalla, lo registramos pero el teardown debe continuar.
                logger.error(f"\n❌ Error al intentar tomar la captura de pantalla de estado final durante el Teardown: {e}", exc_info=False)

        # Detener Tracing y cerrar Contexto
        if context:
            try:
                context.tracing.stop(path=trace_path)
                logger.info(f"\nTracing detenido y guardado en: {trace_path}")
                context.close()
            except Exception as e:
                logger.error(f"\nError al detener el tracing o cerrar el contexto: {e}")
            
        # Cerrar el Navegador
        if browser_instance:
            try:
                browser_instance.close()
                logger.debug(f"\nNavegador {browser_type} cerrado.")
            except Exception as e:
                logger.error(f"\nError al cerrar la instancia del navegador: {e}")
            
        # Renombrar Video
        if page and page.video:
            try:
                video_path = page.video.path()
                
                # 🟢 Incluir el nombre limpio del test en el nombre del video
                # Se asume que safe_test_name ya fue calculado, si no, se recalcula por seguridad.
                if not 'safe_test_name' in locals():
                    safe_test_name = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in request.node.name)
                    
                # 🟢 Formato de nombre del video: {test_name}_{timestamp}.webm
                new_video_name = f"{safe_test_name}_{datetime.now().strftime('%Y%m%d-%H%M%S')}.webm"
                new_video_path = os.path.join(config.VIDEO_DIR, new_video_name)
                
                if os.path.exists(video_path): # Asegurarse de que el video realmente se haya grabado
                    try:
                        os.rename(video_path, new_video_path)
                        logger.info(f"\n🎥 Video renombrado y guardado como: {new_video_path}")
                    except OSError as e:
                        # Error específico de I/O: permisos denegados o archivo todavía en uso (la mejora solicitada)
                        logger.error(
                            f"\n❌ Error de sistema (OSError) al renombrar el video de '{video_path}' a '{new_video_path}'. "
                            f"\nEsto puede ser debido a permisos o el archivo aún está en uso. Detalle: {e}", 
                            exc_info=True
                        )
                    except Exception as e:
                        # Capturar cualquier otro error inesperado durante el renombrado
                        logger.error(
                            f"\n❌ Error inesperado al renombrar el video de '{video_path}' a '{new_video_path}'. Detalle: {e}", 
                            exc_info=True
                        )
                else:
                    # Archivo no existe (Playwright no lo grabó o lo borró) (Mensaje de advertencia detallado)
                    logger.warning(
                        f"\n⚠️ No se encontró el archivo de video temporal en la ruta esperada: {video_path}. "
                        "Esto puede ocurrir si la prueba fue muy corta o falló antes de que Playwright pudiera escribir el archivo."
                    )
            except Exception as e:
                # Capturar errores al intentar acceder a page.video.path() o calcular las rutas
                logger.error(f"\n❌ Error al intentar acceder o procesar la ruta del objeto video: {e}", exc_info=True)
                
        logger.info("\nTeardown del fixture playwright_page finalizado.")
                
@pytest.fixture(scope="session")
def trello_client():
    """Fixture que devuelve una instancia del cliente Trello."""
    return TrelloClient()

# --- Fixture principal de la arquitectura ---
@pytest.fixture(scope="function")
@allure.step("SETUP: Inicializando la BasePage y las Clases de Acciones")
def base_page(playwright_page: Page, request) -> BasePage: 
    """
    Fixture que inicializa la clase BasePage, pasándole el objeto 'page' de Playwright
    y el objeto 'request' de Pytest para que pueda acceder a los fixtures del test.
    """
    logger.debug("\nInicializando BasePage y pasando el objeto request.")
    
    # IMPORTANTE: Pasamos el objeto request.node al constructor de BasePage
    return BasePage(playwright_page, request.node)

# --- Ejemplo de nuevos fixtures de pre-condición ---
@pytest.fixture
@allure.epic("Home Page Tests")
@allure.feature("Módulo Página de Inicio")
@allure.story("Navegación Inicial de la Home Page")
def set_up_Home(base_page: BasePage) -> BasePage:
    """
    Fixture de pre-condición para las pruebas en la página de inicio.
    
    Este fixture garantiza que la página esté en un estado conocido y limpio
    antes de que cada test de la página de inicio comience. Realiza las siguientes acciones:
    
    1. Navega a la URL base de la aplicación.
    2. Valida que la URL actual coincida con la URL base esperada.
    3. Valida que el título de la página sea el correcto.

    Args:
        base_page (BasePage): Instancia de la clase BasePage, lista para la interacción.

    Returns:
        BasePage: La instancia de BasePage ya inicializada y configurada, posicionada
                  en la página de inicio limpia.
    """
    logger.info("SETUP: Ejecutando set_up_Home - Navegación y validación inicial.")
    try:
        # Navega a la URL base
        base_page.navigation.ir_a_url(config.BASE_URL, "ir_a_Home", config.SCREENSHOT_DIR)
    
        base_page.navigation.validar_titulo_de_web("Automation Testing Practice Website for QA and Developers | UI and API", "validar_nombreWeb", config.SCREENSHOT_DIR)
        
        logger.info("\nSETUP: set_up_Home completado con éxito.")
        # Retorna la instancia de BasePage para que el test pueda comenzar sus acciones.
        return base_page
    except Exception as e:
        logger.error(f"\nError crítico durante el SETUP de set_up_Home: {e}", exc_info=True)
        # Se puede lanzar una excepción o marcar un fallo en el setup
        raise
    
@pytest.fixture
@allure.epic("Web Input Tests")
@allure.feature("Módulo de Formularios y Entradas")
@allure.story("Pre-condición: Navegación a Web Input Examples")
def set_up_WebInputs(base_page: BasePage) -> BasePage:
    """
    Fixture de pre-condición para las pruebas específicas de la página 'Web Input Examples'.
    
    Este fixture configura el entorno, asegurando que el navegador esté abierto y
    posicionado en la URL de 'Web Input Examples' antes de que el test comience. 
    
    Realiza las siguientes acciones clave:
    1. Navega a la URL base de la aplicación.
    2. Valida el título de la página principal.
    3. Navega a la sección 'Web Input Examples' haciendo clic en el enlace.
    4. Valida que la URL actual coincida con la URL esperada para Web Inputs.

    Args:
        base_page (BasePage): Instancia de la clase BasePage, lista para la interacción.

    Returns:
        BasePage: La instancia de BasePage ya inicializada y configurada, posicionada
                  en la página 'Web Input Examples' lista para las pruebas.
    """
    logger.info("SETUP: Ejecutando set_up_WebInputs - Navegación y validación inicial.")
    try:
        # Navega a la URL base
        base_page.navigation.ir_a_url(config.BASE_URL, "ir_a_Home", config.SCREENSHOT_DIR)
    
        base_page.navigation.validar_titulo_de_web("Automation Testing Practice Website for QA and Developers | UI and API", "validar_nombreWeb", config.SCREENSHOT_DIR)
        
        # Scroll y clic al enlace para ingresar a Web Input
        base_page.scroll_hasta_elemento(base_page.home.linkWebInput, "scroll_HastaWebInput", config.SCREENSHOT_DIR)
        base_page.element.hacer_clic_en_elemento(base_page.home.linkWebInput, "clic_ingresarAWebInput", config.SCREENSHOT_DIR)
        
        # Valida que haya ingresado correctamente a la página
        base_page.navigation.validar_url_actual(config.WEBINPUT_URL)
        
        logger.info("\nSETUP: set_up_WebInputs completado con éxito.")
        # Retorna la instancia de BasePage para que el test pueda comenzar sus acciones.
        return base_page
    except Exception as e:
        logger.error(f"\nError crítico durante el SETUP de set_up_WebInputs: {e}", exc_info=True)
        # Se puede lanzar una excepción o marcar un fallo en el setup
        raise
    
@pytest.fixture
@allure.epic("Registro")
@allure.feature("Módulo de Registro")
@allure.story("Pre-condición: Navegación a la Página de Registro")
def set_up_RegisterPage(base_page: BasePage) -> BasePage:
    """
    Fixture de pre-condición para las pruebas específicas de la página de Registro (Register Page).
    
    Este fixture configura el entorno:
    1. Asegura que el navegador esté abierto.
    2. Navega a la URL principal (Home).
    3. Hace clic en el enlace para ingresar a la página de Registro.
    4. Valida que la URL actual coincida con la URL esperada para la página de Registro.

    Args:
        base_page (BasePage): Instancia de la clase BasePage.

    Returns:
        BasePage: La instancia de BasePage inicializada y posicionada en la Página de Registro, 
                  lista para que el test comience.
    """
    logger.info("SETUP: Ejecutando set_up_RegisterPage - Navegación y validación inicial.")
    try:
        # Navega a la URL base
        base_page.navigation.ir_a_url(config.BASE_URL, "ir_a_Home", config.SCREENSHOT_DIR)
    
        base_page.navigation.validar_titulo_de_web("Automation Testing Practice Website for QA and Developers | UI and API", "validar_nombreWeb", config.SCREENSHOT_DIR)
        
        # Scroll y clic al enlace para ingresar a la página de Registro
        base_page.scroll_hasta_elemento(base_page.home.linkTestRegister, "scroll_HastaRegisterPage", config.SCREENSHOT_DIR)
        base_page.element.hacer_clic_en_elemento(base_page.home.linkTestRegister, "clic_ingresarRegisterPage", config.SCREENSHOT_DIR)
        
        # Valida que haya ingresado correctamente a la página
        base_page.navigation.validar_url_actual(config.REGISTER_URL)
        
        logger.info("\nSETUP: set_up_RegisterPage completado con éxito.")
        # Retorna la instancia de BasePage para que el test pueda comenzar sus acciones.
        return base_page
    except Exception as e:
        logger.error(f"\nError crítico durante el SETUP de set_up_RegisterPage: {e}", exc_info=True)
        # Se puede lanzar una excepción o marcar un fallo en el setup
        raise
    
@pytest.fixture
@allure.epic("Login")
@allure.feature("Módulo de Login")
@allure.story("Pre-condición: Navegación a la Página de Login")
def set_up_LoginPage(base_page: BasePage) -> BasePage:
    """
    Fixture de pre-condición para las pruebas específicas de la página de Login (Register Page).
    
    Este fixture configura el entorno:
    1. Asegura que el navegador esté abierto.
    2. Navega a la URL principal (Home).
    3. Hace clic en el enlace para ingresar a la página de Login.
    4. Valida que la URL actual coincida con la URL esperada para la página de Login.

    Args:
        base_page (BasePage): Instancia de la clase BasePage.

    Returns:
        BasePage: La instancia de BasePage inicializada y posicionada en la Página de Login, 
                  lista para que el test comience.
    """
    logger.info("SETUP: Ejecutando set_up_LoginPage - Navegación y validación inicial.")
    try:
        # Navega a la URL base
        base_page.navigation.ir_a_url(config.BASE_URL, "ir_a_Home", config.SCREENSHOT_DIR)
    
        base_page.navigation.validar_titulo_de_web("Automation Testing Practice Website for QA and Developers | UI and API", "validar_nombreWeb", config.SCREENSHOT_DIR)
        
        # Scroll y clic al enlace para ingresar a la página de Registro
        base_page.scroll_hasta_elemento(base_page.home.linkTestLogin, "scroll_HastaLoginPage", config.SCREENSHOT_DIR)
        base_page.element.hacer_clic_en_elemento(base_page.home.linkTestLogin, "clic_ingresarLoginPage", config.SCREENSHOT_DIR)
        
        # Valida que haya ingresado correctamente a la página
        base_page.navigation.validar_url_actual(config.LOGIN_URL)
        
        logger.info("\nSETUP: set_up_LoginPage completado con éxito.")
        # Retorna la instancia de BasePage para que el test pueda comenzar sus acciones.
        return base_page
    except Exception as e:
        logger.error(f"\nError crítico durante el SETUP de set_up_LoginPage: {e}", exc_info=True)
        # Se puede lanzar una excepción o marcar un fallo en el setup
        raise
    
# --- HOOKS DE PYTEST PARA REPORTES Y ACCIONES POST-TEST ---
@pytest.fixture(scope="function") 
def test_steps(request) -> Generator[list[str], None, None]:
    """
    Fixtura de alcance de función para recolectar los pasos ejecutados durante la prueba.
    
    Utiliza un generador (`yield`) para tener una fase de 'teardown' segura donde se
    persiste la lista de pasos en el objeto 'item' de Pytest. Esto resuelve el problema
    de que el hook de reporte se ejecuta demasiado tarde (después de la limpieza del fixture).
    
    Yields:
        list[str]: Una lista mutable a la que las acciones de la página pueden agregar pasos.
    """
    logger.info(f"\n[FIXTURE: test_steps] Inicializando lista de pasos para: {request.node.name}")
    
    # 1. Lista que será llenada por _registrar_paso_ejecutado.
    steps_list = []
    
    # 2. El 'yield' devuelve el valor del fixture al test.
    yield steps_list
    
    # 3. ACCIÓN CRÍTICA: TEARDOWN - PERSISTIR EL VALOR en el objeto 'item' (request.node).
    # request.node es el objeto Pytest Function ('item'). Se usa un atributo privado ('_') 
    # para evitar colisiones.
    # [LOGGER AÑADIDO]
    logger.info(f"\n[FIXTURE: test_steps] Teardown: Persistiendo {len(steps_list)} pasos ejecutados en 'request.node._test_steps_result'.")
    request.node._test_steps_result = steps_list
    
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook de Pytest central. Genera el reporte y DESPACHA el resultado a los gestores.
    """
    logger.debug(f"\n[HOOK-MAKER] Entrando a pytest_runtest_makereport (Fase: {call.when}) para: {item.name}")
    
    # 1. Obtener el resultado (reporte)
    outcome = yield
    report = outcome.get_result()

    # 2. Manejo de Fallo en 'call' (ALMACENAMIENTO DE ESTADO)
    if report.when == "call" and report.failed:
        logger.error(f"\n🚨 [HOOK-MAKER] Prueba fallida. Almacenando reporte para procesar en Teardown.")
        item._failed_report = report

    # 3. Despachar a los Handlers en la fase 'teardown'
    # --- Reporte a TRELLO (EXISTENTE) ---
    if report.when == "teardown":
        logger.info(f"\n[HOOK-MAKER] Despachando reportes en fase Teardown para: {item.nodeid}")

        # --- Reporte a TRELLO ---
        if config.TRELLO_REPORTING_ENABLED: 
            _handle_trello_reporting(item, report) 
        else:
            logger.debug("\n[HOOK-MAKER] Reporte a TRELLO desactivado.")
                
        # --- Reporte a JIRA ---
        if config.JIRA_REPORTING_ENABLED: # Asumiendo que esta variable existe en config.py
            _handle_jira_reporting(item, report) # La función ya está importada al inicio
        else:
            logger.debug("\n[HOOK-MAKER] Reporte a JIRA desactivado.")
            
    logger.debug(f"\n[HOOK-MAKER] Saliendo de pytest_runtest_makereport (Fase: {call.when}).")