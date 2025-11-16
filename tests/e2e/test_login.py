import re
import time
import random
import pytest
import os
import json
from playwright.sync_api import Page, expect, Playwright, sync_playwright
from pages.base_page import BasePage
from utils import config
from utils.generador_datos import GeneradorDatos

# Crea una instancia del generador de datos
generador_datos = GeneradorDatos()

def test_verificar_elementos_requeridos_presentes_login(set_up_LoginPage: BasePage) -> None:
    """
    [ID: LG-T001] Verificación de la integridad de la UI de la Página de Login.

    Objetivo:
        Asegurar que, al navegar a la página de Login, todos los elementos 
        críticos del formulario (títulos, etiquetas, campos de entrada de 
        credenciales y el botón principal) estén presentes y visibles, y que 
        el mensaje de feedback (flash message) esté oculto por defecto.

    Flujo:
    
        1. Navegar a la Página de Login (gestionado por la fixture `set_up_LoginPage`).
        2. Desplazamiento (Scroll) hasta el título de la página.
        3. Validar el texto del título principal.
        4. Validar el texto de la descripción de la página.
        5. Verificar la visibilidad de las etiquetas y campos de: Username y Password.
        6. Verificar la visibilidad del botón de Login.
        7. Verificar que el mensaje de *flash* (éxito/error) no esté visible en el estado inicial.
    
    Parámetros:
        set_up_LoginPage (BasePage): Fixture que preconfigura el navegador y 
                                     navega a la página de Login.
                                     
    """
    # La fixture `set_up_LoginPage` garantiza la navegación exitosa.
    base_page = set_up_LoginPage
    
    # PASO 1: Desplazamiento hasta el elemento principal de la página.
    base_page.scroll_hasta_elemento(base_page.login.labelLogin, "scroll_HastaLabelLogin", base_page.SCREENSHOT_BASE_DIR)
    
    # PASO 2 y 3: Validar título y descripción de la página.
    base_page.element.verificar_texto_exacto(base_page.login.labelLogin, 
                                             "Test Login page for Automation Testing Practice",
                                             "verificar_textoExactoLabelTitulo", base_page.SCREENSHOT_BASE_DIR)
    
    texto_descripcion_esperado = (
        """Test Login page""")
    base_page.element.verificar_texto_contenido(base_page.login.labelDescriptionLogin, texto_descripcion_esperado,
                                               "verificarTextoDescripciónLogin", base_page.SCREENSHOT_BASE_DIR
                                               )
    
    # PASO 4: Validar visibilidad de campos de entrada (Username y Password).
    # Username
    base_page.element.validar_elemento_visible(base_page.login.labelUsernameLogin, "verificarLabelUsernameVisible", base_page.SCREENSHOT_BASE_DIR)
    base_page.element.validar_elemento_visible(base_page.login.txtUsernameLogin, "verificarCampoUsernameVisible", base_page.SCREENSHOT_BASE_DIR)
    
    # Password
    base_page.element.validar_elemento_visible(base_page.login.labelPasswordLogin, "verificarLabelPasswordVisible", base_page.SCREENSHOT_BASE_DIR)
    base_page.element.validar_elemento_visible(base_page.login.txtPasswordLogin, "verificarCampoPasswordVisible", base_page.SCREENSHOT_BASE_DIR)
    
    # PASO 5: Validar visibilidad del botón de Login.
    base_page.element.validar_elemento_visible(base_page.login.btnLogin, "verificarBotónLoginVisible", base_page.SCREENSHOT_BASE_DIR)
    
    # PASO 6: Validar que el mensaje de feedback (flash message) no está visible inicialmente.
    base_page.element.validar_elemento_no_visible(base_page.login.flashMessage, "verificarMensajeFlashNoVisible", base_page.SCREENSHOT_BASE_DIR)

def test_login_con_usuario_registrado(set_up_LoginPage: BasePage) -> None:
    """
    [ID: LG-T002] Flujo de Login Exitoso con Credenciales Persistidas.

    Objetivo:
        Verificar la autenticación exitosa de un usuario previamente registrado 
        (cuyas credenciales están guardadas en un JSON), la correcta redirección 
        al dashboard de seguridad y la validación de todos los elementos post-login.

    Flujo:
    
        1. Definir la ruta del archivo JSON con los registros exitosos.
        2. Leer el archivo JSON y seleccionar aleatoriamente las credenciales de un usuario válido.
        3. Rellenar los campos de Username y Password con las credenciales obtenidas.
        4. Hacer clic en el botón de Login.
        5. Validar la redirección a la URL del Dashboard de Usuario.
        6. Verificar el mensaje de éxito (*flash message*) y el saludo personalizado.
        7. Validar la descripción del Dashboard y la visibilidad del botón de Logout.
    
    Parámetros:
        set_up_LoginPage (BasePage): Fixture que preconfigura el navegador y 
                                     navega a la página de Login.
                                     
    """
    
    # La fixture `set_up_LoginPage` garantiza la navegación exitosa.
    base_page = set_up_LoginPage
    
    # 1. Define la ruta para el archivo JSON de registros de usuarios
    file_path_json = os.path.join(config.SOURCE_FILES_DIR_DATA_SOURCE, "registros_exitosos.json")
    
    # 2. Recupera los datos del usuario e inicia el flujo de prueba
    try:
        # Intenta leer todos los registros del archivo JSON
        registros = base_page.file.leer_json(
            json_file_path=file_path_json, 
            nombre_paso="Leer datos de usuario para Login"
        )
        
        # Validación: Asegura que la lista de registros no esté vacía
        if not registros or not isinstance(registros, list):
            base_page.logger.error(f"\n❌ El archivo JSON no contiene una lista de datos válida en: {file_path_json}")
            # Fallo explícito si no hay datos para el login
            pytest.fail("El archivo de registros de usuarios está vacío o en formato incorrecto.")
            
        # Selecciona un usuario aleatorio de la lista de registros
        datos_usuario = random.choice(registros)
        
        # 3. Interacción con el formulario de Login
        base_page.scroll_hasta_elemento(base_page.login.labelLogin, "scroll_HastaLabelLogin", base_page.SCREENSHOT_BASE_DIR)
        
        base_page.element.rellenar_campo_de_texto(base_page.login.txtUsernameLogin, datos_usuario["username"], "escribir_campoUsername", base_page.SCREENSHOT_BASE_DIR)
        base_page.element.rellenar_campo_de_texto(base_page.login.txtPasswordLogin, datos_usuario["password"], "escribir_campoPassword", base_page.SCREENSHOT_BASE_DIR)
        base_page.element.hacer_clic_en_elemento(base_page.login.btnLogin, "clic_botónLogin", base_page.SCREENSHOT_BASE_DIR)
        
        # 4. Validaciones post-Login (Dashboard)
        
        # Valida que la URL sea la del Dashboard
        base_page.navigation.validar_url_actual(config.USERDASHBOARD_URL)
        
        # Valida el mensaje de éxito (flash message)
        base_page.element.verificar_texto_exacto(base_page.userdashboard.flashMessage, "You logged into a secure area!", "verificarMensajeLoginExitoso", base_page.SCREENSHOT_BASE_DIR)
        
        # Valida el saludo personalizado al usuario
        base_page.element.verificar_texto_exacto(base_page.userdashboard.labelWelcome, f"Hi, {datos_usuario["username"]}!", "verificarSaludoAUsuario", base_page.SCREENSHOT_BASE_DIR)
        
        # Valida la descripción del Dashboard
        base_page.element.verificar_texto_exacto(base_page.userdashboard.labelDescriptionDashboard, 
                                                "Welcome to the Secure Area. When you are done click logout below.",
                                                "verificarDescripciónDashboard", base_page.SCREENSHOT_BASE_DIR)
        
        # Valida que el botón de Logout esté visible
        base_page.element.validar_elemento_visible(base_page.userdashboard.btnLogout, "validar_botónLogoutVisible", base_page.SCREENSHOT_BASE_DIR)
        
    except Exception as e:
        # Manejo de errores en caso de fallo en la lectura de archivos o flujo
        base_page.logger.error(f"\n❌ Error al leer o procesar el archivo JSON: {e}")
        pytest.fail(f"Fallo crítico al cargar datos de credenciales. Error: {e}")
        
def test_login_con_usuario_no_registrado(set_up_LoginPage: BasePage) -> None:
    """
    [ID: LG-T003] Flujo de Login Fallido con Credenciales No Registradas.

    Objetivo:
        Verificar que el sistema rechace el inicio de sesión cuando se utilizan 
        credenciales generadas dinámicamente que no han sido previamente registradas,
        mostrando un mensaje de error explícito y manteniendo al usuario en la página de Login.

    Flujo:
    
        1. Generar un conjunto de credenciales válidas pero no registradas (usuario y contraseña).
        2. Rellenar los campos de Username y Password con estos datos no registrados.
        3. Hacer clic en el botón de Login.
        4. **Validación (Permanencia):** Verificar que la URL actual sigue siendo la de Login.
        5. **Validación (Error):** Verificar que se muestre el mensaje de error "Username/Password invalid" 
           o similar (*flash message*).
    
    Parámetros:
        set_up_LoginPage (BasePage): Fixture que preconfigura el navegador y 
                                     navega a la página de Login.
                                     
    """
    
    # La fixture `set_up_LoginPage` garantiza la navegación exitosa.
    base_page = set_up_LoginPage
    
    # 1. Genera datos de usuario válidos (pero no registrados en el sistema)
    datos_usuario = generador_datos.generar_usuario_valido()
    
    # 2. Rellenar campos del formulario de Login
    base_page.scroll_hasta_elemento(base_page.login.labelLogin, "scroll_HastaLabelLogin", base_page.SCREENSHOT_BASE_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.login.txtUsernameLogin, datos_usuario["username"], "escribir_campoUsernameNoRegistrado", base_page.SCREENSHOT_BASE_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.login.txtPasswordLogin, datos_usuario["password"], "escribir_campoPasswordNoRegistrado", base_page.SCREENSHOT_BASE_DIR)
    
    # 3. Intentar hacer clic en el botón de Login
    base_page.element.hacer_clic_en_elemento(base_page.login.btnLogin, "clic_botónLoginConCredencialesInvalidas", base_page.SCREENSHOT_BASE_DIR)
    
    # 4. Validar que el usuario permanece en la misma pantalla de Login (URL)
    base_page.navigation.validar_url_actual(config.LOGIN_URL)
    
    # 5. Validar mensaje de error de usuario no registrado o credenciales incorrectas
    base_page.element.verificar_texto_exacto(base_page.login.flashMessage, "Username/Passoword invalid!", "verificar_MensajeError", base_page.SCREENSHOT_BASE_DIR)
    
def test_login_con_usuario_con_campos_vacios(set_up_LoginPage: BasePage) -> None:
    """
    [ID: LG-T004] Flujo de Login Fallido al Enviar Campos Vacíos.

    Objetivo:
        Verificar que el sistema impida el inicio de sesión cuando el usuario intenta
        enviar el formulario con los campos de Username y Password vacíos, 
        mostrando un mensaje de error específico que exige completar todos los campos.

    Flujo:
    
        1. Verificar el estado inicial de los campos Username y Password (deben estar vacíos).
        2. Hacer clic en el botón de Login sin ingresar ningún dato.
        3. **Validación (Permanencia):** Verificar que la URL actual sigue siendo la de Login.
        4. **Validación (Error):** Verificar que se muestre el mensaje de error "All fields are required.".
    
    Parámetros:
        set_up_LoginPage (BasePage): Fixture que preconfigura el navegador y 
                                     navega a la página de Login.
                                     
    """
    # La fixture `set_up_LoginPage` garantiza la navegación exitosa.
    base_page = set_up_LoginPage
    
    # 1. Validar que los campos Username y Password están inicialmente vacíos
    base_page.scroll_hasta_elemento(base_page.login.labelLogin, "scroll_HastaLabelLogin", base_page.SCREENSHOT_BASE_DIR)
    base_page.element.validar_elemento_vacio(base_page.login.txtUsernameLogin, "validar_UsernameVacio", base_page.SCREENSHOT_BASE_DIR)
    base_page.element.validar_elemento_vacio(base_page.login.txtPasswordLogin, "validar_PasswordVacio", base_page.SCREENSHOT_BASE_DIR)
    
    # 2. Proceder con el intento de login con campos vacíos
    base_page.element.hacer_clic_en_elemento(base_page.login.btnLogin, "clic_botónLoginConCamposVacios", base_page.SCREENSHOT_BASE_DIR)
    
    # 3. Validar que el usuario permanece en la misma pantalla de Login (URL)
    base_page.navigation.validar_url_actual(config.LOGIN_URL)
    
    # 4. Validar mensaje de error de campos obligatorios
    base_page.element.verificar_texto_exacto(base_page.login.flashMessage, "All fields are required.", "verificar_MensajeErrorCamposVacios", base_page.SCREENSHOT_BASE_DIR)
    
def test_login_con_usuario_y_sin_password(set_up_LoginPage: BasePage) -> None:
    """
    [ID: LG-T005] Flujo de Login Fallido con Contraseña Vacía.

    Objetivo:
        Verificar que el sistema rechace el intento de inicio de sesión cuando solo se 
        proporciona un Username/Email válido, dejando el campo Password vacío. 
        Se espera un mensaje de error que exija completar todos los campos.

    Prerrequisito:
        Un usuario debe existir previamente y sus credenciales deben estar guardadas 
        en el archivo 'registros_exitosos.json'.

    Flujo:
    
        1. Cargar las credenciales de un usuario registrado desde el archivo JSON.
        2. Rellenar el campo Username con el email/usuario cargado.
        3. Verificar que el campo Password permanezca vacío.
        4. Hacer clic en el botón de Login.
        5. **Validación (Permanencia):** Verificar que la URL actual siga siendo la de Login.
        6. **Validación (Error):** Verificar que se muestre el mensaje de error "All fields are required.".
    
    Parámetros:
        set_up_LoginPage (BasePage): Fixture que preconfigura el navegador y 
                                     navega a la página de Login.
                                     
    """
    # La fixture `set_up_LoginPage` garantiza la navegación exitosa.
    base_page = set_up_LoginPage
    
    # 1. Define la ruta absoluta para el archivo JSON de registros
    file_path_json = os.path.join(config.SOURCE_FILES_DIR_DATA_SOURCE, "registros_exitosos.json")
    
    try:
        # 2. Recupera los datos del usuario registrado utilizando la función leer_json
        registros = base_page.file.leer_json(
            json_file_path=file_path_json, 
            nombre_paso="Leer datos de usuario para Login sin Password"
        )
        
        # Validación: Asegura que la lista de registros no esté vacía y sea una lista
        if not registros or not isinstance(registros, list):
            base_page.logger.error(f"\n❌ El archivo JSON no contiene una lista de datos válida en: {file_path_json}")
            # Fallo explícito
            pytest.fail("El archivo de registros de usuarios está vacío o en formato incorrecto.")
            
        # Selecciona un diccionario de usuario al azar de la lista para usar su Username.
        datos_usuario = random.choice(registros)
        
        # 3. Rellenar el campo Username
        base_page.scroll_hasta_elemento(base_page.login.labelUsernameLogin, "scroll_HastaLabelUsername", base_page.SCREENSHOT_BASE_DIR)
        base_page.element.rellenar_campo_de_texto(
            base_page.login.txtUsernameLogin, 
            datos_usuario["username"], 
            "escribir_campoUsername",
            base_page.SCREENSHOT_BASE_DIR
        )
        
        # 4. Validar que el campo Password está vacío (se deja deliberadamente sin rellenar)
        base_page.element.validar_elemento_vacio(base_page.login.txtPasswordLogin, "validar_PasswordVacío", base_page.SCREENSHOT_BASE_DIR)
        
        # 5. Intentar hacer clic en Login
        base_page.element.hacer_clic_en_elemento(base_page.login.btnLogin, "clic_botónLoginSinPassword", base_page.SCREENSHOT_BASE_DIR)
        
        # 6. Validar que la URL no ha cambiado (permanece en la pantalla de Login)
        base_page.navigation.validar_url_actual(config.LOGIN_URL)
        
        # 7. Validar mensaje de error de campos obligatorios
        base_page.element.verificar_texto_exacto(
            base_page.login.flashMessage, 
            "All fields are required.", 
            "verificar_MensajeErrorCamposObligatorios",
            base_page.SCREENSHOT_BASE_DIR
        )
    
    except Exception as e:
        base_page.logger.error(f"\n❌ Error al leer o procesar el archivo JSON: {e}")
        pytest.fail(f"Fallo crítico al cargar datos de credenciales. Error: {e}")
        
def test_login_con_password_y_sin_username(set_up_LoginPage: BasePage) -> None:
    """
    [ID: LG-T006] Flujo de Login Fallido con Username Vacío.

    Objetivo:
        Verificar que el sistema rechace el intento de inicio de sesión cuando solo se 
        proporciona la Password válida, dejando el campo Username vacío. 
        Se espera un mensaje de error que exija completar todos los campos.

    Prerrequisito:
        Un usuario debe existir previamente y sus credenciales deben estar guardadas 
        en el archivo 'registros_exitosos.json'.

    Flujo:
    
        1. Cargar las credenciales de un usuario registrado desde el archivo JSON.
        2. Verificar que el campo Username permanezca vacío.
        3. Rellenar el campo Password con la contraseña cargada.
        4. Hacer clic en el botón de Login.
        5. **Validación (Permanencia):** Verificar que la URL actual siga siendo la de Login.
        6. **Validación (Error):** Verificar que se muestre el mensaje de error "All fields are required.".
    
    Parámetros:
        set_up_LoginPage (BasePage): Fixture que preconfigura el navegador y 
                                     navega a la página de Login.
                                     
    """
    # La fixture `set_up_LoginPage` garantiza la navegación exitosa.
    base_page = set_up_LoginPage
    
    # 1. Define la ruta absoluta para el archivo JSON de registros
    file_path_json = os.path.join(config.SOURCE_FILES_DIR_DATA_SOURCE, "registros_exitosos.json")
    
    try:
        # 2. Recupera los datos del usuario registrado utilizando la función leer_json
        registros = base_page.file.leer_json(
            json_file_path=file_path_json, 
            nombre_paso="Leer datos de usuario para Login sin Username"
        )
        
        # Validación: Asegura que la lista de registros no esté vacía y sea una lista
        if not registros or not isinstance(registros, list):
            base_page.logger.error(f"\n❌ El archivo JSON no contiene una lista de datos válida en: {file_path_json}")
            # Fallo explícito
            pytest.fail("El archivo de registros de usuarios está vacío o en formato incorrecto.")
            
        # Selecciona un diccionario de usuario al azar de la lista para usar su Password.
        datos_usuario = random.choice(registros)
        
        # 3. Validar que el campo Username está vacío (se deja deliberadamente sin rellenar)
        base_page.scroll_hasta_elemento(base_page.login.labelUsernameLogin, "scroll_HastaLabelUsername", base_page.SCREENSHOT_BASE_DIR)
        base_page.element.validar_elemento_vacio(base_page.login.txtUsernameLogin, "validar_UsernameVacío", base_page.SCREENSHOT_BASE_DIR)
        
        # 4. Rellenar el campo Password
        base_page.element.rellenar_campo_de_texto(
            base_page.login.txtPasswordLogin, 
            datos_usuario["password"], 
            "escribir_campoPassword",
            base_page.SCREENSHOT_BASE_DIR
        )
        
        # 5. Intentar hacer clic en Login
        base_page.element.hacer_clic_en_elemento(base_page.login.btnLogin, "clic_botónLoginSinUsername", base_page.SCREENSHOT_BASE_DIR)
        
        # 6. Validar que la URL no ha cambiado (permanece en la pantalla de Login)
        base_page.navigation.validar_url_actual(config.LOGIN_URL)
        
        # 7. Validar mensaje de error de campos obligatorios
        base_page.element.verificar_texto_exacto(
            base_page.login.flashMessage, 
            "All fields are required.", 
            "verificar_MensajeErrorCamposObligatorios",
            base_page.SCREENSHOT_BASE_DIR
        )
    
    except Exception as e:
        base_page.logger.error(f"\n❌ Error al leer o procesar el archivo JSON: {e}")
        pytest.fail(f"Fallo crítico al cargar datos de credenciales. Error: {e}")
        
def test_cerrar_mensaje_flash(set_up_LoginPage: BasePage) -> None:
    """
    [ID: LG-T007] Prueba de Usabilidad: Cierre Exitoso del Mensaje de Error Flash.

    Objetivo:
        Verificar que el usuario pueda cerrar el mensaje de error o notificación
        ('Flash Message') que aparece después de una acción fallida (como intentar
        iniciar sesión sin credenciales), y que el mensaje desaparezca de la UI.

    Prerrequisito:
        El botón de Login debe estar operativo y el sistema debe responder
        con un mensaje de error si los campos están vacíos.

    Flujo:
    
        1. Asegurar que los campos Username y Password estén vacíos (estado inicial).
        2. Hacer clic en el botón de Login para forzar la aparición del mensaje de error.
        3. **Validación (Aparición):** Verificar que el mensaje flash de error sea visible.
        4. Hacer clic en el botón de cierre (usualmente 'X') del mensaje flash.
        5. **Validación (Desaparición):** Verificar que el mensaje flash ya no sea visible en la UI.
    
    Parámetros:
        set_up_LoginPage (BasePage): Fixture que preconfigura el navegador y 
                                     navega a la página de Login.
                                     
    """
    # La fixture `set_up_LoginPage` asegura la navegación exitosa a la página de Login.
    base_page = set_up_LoginPage
    
    # 1. Scroll hasta el formulario y validar que los campos de Username y Password estén vacíos
    base_page.scroll_hasta_elemento(base_page.login.labelUsernameLogin, "scroll_HastaLabelUsername", base_page.SCREENSHOT_BASE_DIR)
    base_page.element.validar_elemento_vacio(base_page.login.txtUsernameLogin, "validar_UsernameVacio", base_page.SCREENSHOT_BASE_DIR)
    base_page.element.validar_elemento_vacio(base_page.login.txtPasswordLogin, "validar_PasswordVacio", base_page.SCREENSHOT_BASE_DIR)
    
    # 2. Hacer clic en Login con campos vacíos para disparar el mensaje de error
    base_page.element.hacer_clic_en_elemento(base_page.login.btnLogin, "click_botónLoginCamposVacios", base_page.SCREENSHOT_BASE_DIR)
    
    # 3. Validar que la URL permanezca en la página de Login (comportamiento esperado tras fallo)
    base_page.navigation.validar_url_actual(config.LOGIN_URL)
    
    # 4. Validar que el mensaje flash de error sea visible
    base_page.element.validar_elemento_visible(base_page.login.flashMessage, "verificar_MensajeFlashVisible", base_page.SCREENSHOT_BASE_DIR)
    
    # 5. Hacer clic en el botón de cierre del mensaje flash
    base_page.element.hacer_clic_en_elemento(base_page.login.btnCerrarFlashMessage, "clic_CerrarMensajeFlash", base_page.SCREENSHOT_BASE_DIR)
    
    # 6. Validar que el mensaje flash ya no sea visible
    base_page.element.validar_elemento_no_visible(base_page.login.flashMessage, "verificar_MensajeFlashNoVisible", base_page.SCREENSHOT_BASE_DIR)
    
def test_login_usuario_con_password_incorrecta(set_up_LoginPage: BasePage) -> None:
    """
    [ID: LG-T008] Prueba el inicio de sesión fallido con credenciales incorrectas.

    Objetivo:
        Verificar que el sistema rechace el inicio de sesión cuando se utiliza un
        Username válido (de un usuario previamente registrado) combinado con una
        Password incorrecta, y que se muestre el mensaje de error adecuado.

    Flujo:
    
        1. Carga un diccionario de datos de un usuario previamente registrado 
           desde el archivo 'registros_exitosos.json'.
        2. Genera una contraseña segura al azar que será la credencial incorrecta.
        3. Rellena el campo 'Username' con el dato válido del usuario.
        4. Rellena el campo 'Password' con la contraseña incorrecta.
        5. Hace clic en el botón 'Login'.
        6. **Validación 1 (Mensaje de Error):** Verifica que el mensaje de flash
           "Username/Passoword invalid!" sea visible.
        7. **Validación 2 (Redirección):** Confirma que la URL actual permanece
           en la página de Login, indicando que el acceso fue denegado.

    Parámetros:
        set_up_LoginPage (BasePage): Fixture que inicializa el navegador y navega
                                     a la página de Login.

    Retorna:
        None: La prueba pasa si se cumplen ambas validaciones de error.
        
    """
    # La fixture `set_up_LoginPage` asegura la navegación exitosa a la página de Login.
    base_page = set_up_LoginPage
    
    file_path_json = os.path.join(config.SOURCE_FILES_DIR_DATA_SOURCE, "registros_exitosos.json")
    
    try:
        # Paso 1: Intentar leer los datos de usuarios registrados desde el archivo JSON
        registros = base_page.file.leer_json(
            json_file_path=file_path_json, 
            nombre_paso="Leer datos de usuarios registrados"
        )
        
        if not registros or not isinstance(registros, list):
            base_page.logger.error(f"\n❌ El archivo JSON no contiene una lista de datos válida en: {file_path_json}")
            pytest.fail("El archivo de registros de usuarios está vacío o en formato incorrecto.")
            
        # Paso 2: Selecciona un diccionario de usuario al azar de la lista para usar su Username.
        datos_usuario = random.choice(registros)
    
        # Genera una contraseña aleatoria para simular un intento fallido.
        diferenteConfirmacion = generador_datos.generar_password_segura()
        
        # Paso 3: Rellenar el campo Username con el dato válido del usuario registrado
        base_page.scroll_hasta_elemento(base_page.login.labelUsernameLogin, "Scroll_HastaLabelUsername", base_page.SCREENSHOT_BASE_DIR)
        base_page.element.rellenar_campo_de_texto(base_page.login.txtUsernameLogin, datos_usuario["username"], "Escribir_UsernameValido", base_page.SCREENSHOT_BASE_DIR)

        # Paso 4: Rellenar el campo Password con la contraseña incorrecta generada al azar
        base_page.element.rellenar_campo_de_texto(base_page.login.txtPasswordLogin, diferenteConfirmacion, "Escribir_PasswordIncorrecta", base_page.SCREENSHOT_BASE_DIR)
        
        # Paso 5: Hacer clic en el botón de Login
        base_page.element.hacer_clic_en_elemento(base_page.login.btnLogin, "Click_BotónLogin_PasswordIncorrecta", base_page.SCREENSHOT_BASE_DIR)
        
        # Paso 6: Validar el mensaje de error de credenciales inválidas
        base_page.element.verificar_texto_exacto(base_page.login.flashMessage, "Username/Passoword invalid!", "Verificar_MensajeErrorCredenciales", base_page.SCREENSHOT_BASE_DIR)
        
        # Paso 7: Validar que el usuario no fue redirigido y permanece en la página de Login
        base_page.navigation.validar_url_actual(config.LOGIN_URL)
        
    except Exception as e:
        # Manejo de error crítico si falla la carga o el procesamiento de datos iniciales
        base_page.logger.error(f"\n❌ Error al leer o procesar el archivo JSON: {e}")
        pytest.fail(f"Fallo crítico al cargar datos de credenciales. Error: {e}")
        
def test_ir_a_otro_modulo_con_login_exitoso(set_up_LoginPage: BasePage) -> None:
    """
    [ID: LG-T009] Prueba la persistencia de la sesión y el acceso a módulos
    después de un inicio de sesión exitoso.

    Objetivo:
        Verificar el flujo completo de autenticación (Login), la validación de 
        la sesión en el Dashboard, la navegación a la página de Home, y la
        correcta restricción de acceso al módulo de Login mientras la sesión
        permanece activa.

    Flujo:
    
        1. Carga un usuario válido desde 'registros_exitosos.json'.
        2. Inicia sesión exitosamente con las credenciales cargadas.
        3. **Validaciones Post-Login:**
           a. Verifica la redirección a la URL del Dashboard.
           b. Verifica el mensaje flash de "Login Exitoso".
           c. Verifica el mensaje de bienvenida con el nombre de usuario.
           d. Verifica la visibilidad del botón de Logout.
        4. Navega a la página de Home haciendo clic en un enlace de navegación (e.g., 'Go Home').
        5. **Validaciones en Home:**
           a. Verifica la redirección a la URL base.
           b. Verifica la visibilidad de los enlaces principales (Web Input, Test Login, etc.).
        6. Intenta navegar nuevamente al módulo de Login (linkTestLogin).
        7. **Validación (Restricción de Acceso):** Verifica que el sistema redirija al usuario 
           nuevamente al Dashboard y muestre un mensaje de error indicando que ya ha iniciado sesión.
    
    Parámetros:
        set_up_LoginPage (BasePage): Fixture que inicializa el navegador y navega
                                     a la página de Login.

    Retorna:
        None: La prueba pasa si se cumplen todas las validaciones de redirección y mensajes.
        
    """
    # La fixture `set_up_LoginPage` asegura la navegación exitosa a la página de Login.
    base_page = set_up_LoginPage
    
    file_path_json = os.path.join(config.SOURCE_FILES_DIR_DATA_SOURCE, "registros_exitosos.json")
    
    try:
        # 1. Cargar datos de un usuario previamente registrado
        registros = base_page.file.leer_json(
            json_file_path=file_path_json, 
            nombre_paso="Leer datos de usuario válido para Login"
        )
        
        if not registros or not isinstance(registros, list):
            base_page.logger.error(f"\n❌ El archivo JSON no contiene una lista de datos válida en: {file_path_json}")
            pytest.fail("El archivo de registros de usuarios está vacío o en formato incorrecto.")
            
        # 2. Seleccionar un usuario al azar
        datos_usuario = random.choice(registros)
        
        # 3. Iniciar sesión
        base_page.scroll_hasta_elemento(base_page.login.labelUsernameLogin, "Scroll_HastaLabelUsername", base_page.SCREENSHOT_BASE_DIR)
        base_page.element.rellenar_campo_de_texto(base_page.login.txtUsernameLogin, datos_usuario["username"], "Escribir_UsernameValido", base_page.SCREENSHOT_BASE_DIR)
        base_page.element.rellenar_campo_de_texto(base_page.login.labelPasswordLogin, datos_usuario["password"], "Escribir_PasswordValida", base_page.SCREENSHOT_BASE_DIR)
        base_page.element.hacer_clic_en_elemento(base_page.login.btnLogin, "Click_BotónLogin", base_page.SCREENSHOT_BASE_DIR)
        
        # 4. Validaciones Post-Login Exitoso (Dashboard)
        base_page.navigation.validar_url_actual(config.USERDASHBOARD_URL)
        base_page.element.verificar_texto_exacto(base_page.userdashboard.flashMessage, "You logged into a secure area!", "verificarMensajeLoginExitoso", base_page.SCREENSHOT_BASE_DIR)
        base_page.element.verificar_texto_exacto(base_page.userdashboard.labelWelcome, f"Hi, {datos_usuario['username']}!", "verificarSaludoAUsuario", base_page.SCREENSHOT_BASE_DIR)
        base_page.element.validar_elemento_visible(base_page.userdashboard.btnLogout, "validar_botónLogoutVisible", base_page.SCREENSHOT_BASE_DIR)
        
        # 5. Navegar a Home
        base_page.element.hacer_clic_en_elemento(base_page.userdashboard.linkGoHome, "clic_LinkHome", base_page.SCREENSHOT_BASE_DIR)
        
        # 6. Validaciones en Home
        base_page.navigation.validar_url_actual(config.BASE_URL)
        base_page.scroll_hasta_elemento(base_page.home.linkWebInput, "scroll_HastaWebInput", base_page.SCREENSHOT_BASE_DIR)
        base_page.element.validar_elemento_visible(base_page.home.linkWebInput, "validadVisibilidad_WebInput", base_page.SCREENSHOT_BASE_DIR)
        base_page.element.validar_elemento_visible(base_page.home.linkTestLogin, "validadVisibilidad_TestLogin", base_page.SCREENSHOT_BASE_DIR)
        base_page.element.validar_elemento_visible(base_page.home.linkTestRegister, "validadVisibilidad_TestRegister", base_page.SCREENSHOT_BASE_DIR)
        base_page.element.validar_elemento_visible(base_page.home.linkDynamicTable, "validadVisibilidad_DynamicTable", base_page.SCREENSHOT_BASE_DIR)
        
        # 7. Intentar navegar a Login Estando Ya Autenticado
        base_page.element.hacer_clic_en_elemento(base_page.home.linkTestLogin, "clic_linkTestLogin_SessionActiva", base_page.SCREENSHOT_BASE_DIR)
        
        # 8. Validación de Restricción: Debería ser redirigido al Dashboard
        base_page.navigation.validar_url_actual(config.USERDASHBOARD_URL)
        
        # 9. Validación de Mensaje: El sistema informa que el usuario ya está logueado
        base_page.element.verificar_texto_exacto(base_page.userdashboard.flashMessage, 
                                                "You're logged in. Please log out before logging in as a different user",
                                                "verificarTextoMensajeFlash_YaLogueado",
                                                base_page.SCREENSHOT_BASE_DIR)                                       
    except Exception as e:
        # Manejo de error crítico si falla la carga o el procesamiento de datos iniciales
        base_page.logger.error(f"\n❌ Error al leer o procesar el archivo JSON: {e}")
        pytest.fail(f"Fallo crítico al cargar datos de credenciales. Error: {e}")
        
def test_hacer_logout_exitoso(set_up_LoginPage: BasePage) -> None:
    """
    [ID: LG-T010] Prueba el cierre de sesión (Logout) exitoso desde el Dashboard.

    Objetivo:
        Verificar que el botón de Logout funcione correctamente, finalice la sesión
        del usuario y lo redirija de vuelta a la página de Login, mostrando el
        mensaje de cierre de sesión exitoso.

    Flujo:
    
        1. Carga un usuario válido desde 'registros_exitosos.json'.
        2. Inicia sesión exitosamente con las credenciales cargadas.
        3. **Validaciones Post-Login:** Confirma el acceso al Dashboard.
        4. Hace clic en el botón 'Logout' en el Dashboard.
        5. **Validación 1 (Redirección):** Verifica que la URL actual sea la de Login.
        6. **Validación 2 (Mensaje de Éxito):** Verifica que se muestre el mensaje flash
           "You logged out of the secure area!".
        7. **Validación 3 (Estado de la UI):** Verifica la visibilidad de los campos
           del formulario de Login y que estos estén vacíos, confirmando que el
           sistema está listo para un nuevo inicio de sesión.

    Parámetros:
        set_up_LoginPage (BasePage): Fixture que inicializa el navegador y navega
                                     a la página de Login.

    Retorna:
        None: La prueba pasa si se cumplen todas las validaciones de cierre de sesión.
        
    """
    # Inicializa la instancia de BasePage proporcionada por el fixture.
    base_page = set_up_LoginPage
    
    # Define la ruta al archivo JSON de registros exitosos.
    file_path_json = os.path.join(config.SOURCE_FILES_DIR_DATA_SOURCE, "registros_exitosos.json")
    
    try:
        # 1. Cargar datos de credenciales válidas desde el archivo JSON
        registros = base_page.file.leer_json(
            json_file_path=file_path_json, 
            nombre_paso="Leer datos de usuario válido para Login"
        )
        
        if not registros or not isinstance(registros, list):
            base_page.logger.error(f"\n❌ El archivo JSON no contiene una lista de datos válida en: {file_path_json}")
            pytest.fail("El archivo de registros de usuarios está vacío o en formato incorrecto.")
            
        # 2. Seleccionar un usuario al azar para el Login
        datos_usuario = random.choice(registros)
        
        # 3. Iniciar sesión exitosamente con las credenciales cargadas
        base_page.scroll_hasta_elemento(base_page.login.labelUsernameLogin, "Scroll_HastaLabelUsername", base_page.SCREENSHOT_BASE_DIR)
        base_page.element.rellenar_campo_de_texto(base_page.login.txtUsernameLogin, datos_usuario["username"], "Escribir_UsernameValido", base_page.SCREENSHOT_BASE_DIR)
        base_page.element.rellenar_campo_de_texto(base_page.login.labelPasswordLogin, datos_usuario["password"], "Escribir_PasswordValida", base_page.SCREENSHOT_BASE_DIR)
        base_page.element.hacer_clic_en_elemento(base_page.login.btnLogin, "Click_BotónLogin", base_page.SCREENSHOT_BASE_DIR)
        
        # 4. Validaciones Post-Login: Confirmar el acceso al Dashboard
        base_page.navigation.validar_url_actual(config.USERDASHBOARD_URL)
        base_page.element.verificar_texto_exacto(base_page.userdashboard.flashMessage, "You logged into a secure area!", "verificarMensajeLoginExitoso", base_page.SCREENSHOT_BASE_DIR)
        base_page.element.verificar_texto_exacto(base_page.userdashboard.labelWelcome, f"Hi, {datos_usuario['username']}!", "verificarSaludoAUsuario", base_page.SCREENSHOT_BASE_DIR)
        
        # 5. Ejecutar Logout: Clic en el botón 'Logout'
        base_page.element.hacer_clic_en_elemento(base_page.userdashboard.btnLogout, "clic_botónLogout", base_page.SCREENSHOT_BASE_DIR)
        
        # 6. Validación 1 (Redirección): Verificar regreso a la URL de Login
        base_page.navigation.validar_url_actual(config.LOGIN_URL)
        
        # Validación 2 (Mensaje de Éxito): Verificar el mensaje flash de cierre de sesión
        base_page.element.verificar_texto_exacto(base_page.login.flashMessage, 
                                                 "You logged out of the secure area!",
                                                 "verificarTextoMensajeFlash_Logout",
                                                 base_page.SCREENSHOT_BASE_DIR)
        
        # 7. Validación 3 (Estado de la UI): Verificar que el formulario de Login esté listo
        # Visibilidad de elementos del Login (formulario listo para nuevo acceso)
        base_page.element.validar_elemento_visible(base_page.login.labelUsernameLogin, "verificarLabelUsernameVisible", base_page.SCREENSHOT_BASE_DIR)
        base_page.element.validar_elemento_visible(base_page.login.txtUsernameLogin, "verificarCampoUsernameVisible", base_page.SCREENSHOT_BASE_DIR)
        base_page.element.validar_elemento_vacio(base_page.login.txtUsernameLogin, "verificarCampoUsernameVacío", base_page.SCREENSHOT_BASE_DIR)
        base_page.element.validar_elemento_visible(base_page.login.labelPasswordLogin, "verificarLabelPasswordVisible", base_page.SCREENSHOT_BASE_DIR)
        base_page.element.validar_elemento_visible(base_page.login.txtPasswordLogin, "verificarCampoPasswordVisible", base_page.SCREENSHOT_BASE_DIR)
        base_page.element.validar_elemento_vacio(base_page.login.txtPasswordLogin, "verificarCampoPasswordVacío", base_page.SCREENSHOT_BASE_DIR)
        base_page.element.validar_elemento_visible(base_page.login.btnLogin, "verificarBotónLoginVisible", base_page.SCREENSHOT_BASE_DIR)
        
        # Verificación de que los elementos del Dashboard ya no están visibles
        base_page.element.validar_elemento_no_visible(base_page.userdashboard.labelDescriptionDashboard, "verificarDescripciónDashboardNoVisible", base_page.SCREENSHOT_BASE_DIR)
        base_page.element.validar_elemento_no_visible(base_page.userdashboard.btnLogout, "verificarLogoutButtonNoVisible", base_page.SCREENSHOT_BASE_DIR)
        
        
    except Exception as e:
        # Manejo de error crítico si falla la carga o el procesamiento de datos iniciales.
        base_page.logger.error(f"\n❌ Error al leer o procesar el archivo JSON: {e}")
        pytest.fail(f"Fallo crítico al cargar datos de credenciales. Error: {e}")