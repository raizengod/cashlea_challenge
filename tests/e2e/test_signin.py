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

def test_signin_con_usuario_registrado(base_page: BasePage) -> None:
    """
    [ID: LG-T001] Prueba de Inicio de Sesión Exitoso con Usuario Registrado.
    
    Verifica la funcionalidad de inicio de sesión (Sign In) utilizando credenciales 
    válidas de un usuario registrado en el sistema. Los datos del usuario (email y
    contraseña) se leen de forma aleatoria desde un archivo de registros JSON.
    
    Pasos:
    1. Navegar a la URL base de la aplicación y validar el título de la web.
    2. Verificar la visibilidad de elementos clave en la página de inicio (Home).
    3. Hacer clic en el enlace 'Sign In'.
    4. Leer un registro de usuario aleatorio desde 'registros_exitosos.json'.
    5. Rellenar los campos de Email y Password con las credenciales obtenidas.
    6. Hacer clic en el botón 'Sign In'.
    
    Resultado Esperado:
    El usuario debe iniciar sesión exitosamente y ser redirigido a su *Feed* o 
    página principal dentro de la aplicación (la validación de este estado 
    final es el paso implícito después de hacer clic en 'Sign In').
    """
    
    # Navega a la URL base
    base_page.navigation.ir_a_url(config.BASE_URL, "inicio_test", config.SCREENSHOT_DIR)
    
    base_page.navigation.validar_titulo_de_web("Home — Conduit", "validar_titulo_de_web", config.SCREENSHOT_DIR)
    
    #Verificando que el home page se haya cargado correctamente
    base_page.element.validar_elemento_visible(base_page.home.addHeader, "validar_addHeader_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.home.bannerHome, "validar_bannerHome_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.home.globalFeedHome, "validar_globalFeed_visible", config.SCREENSHOT_DIR)
    
    #Ir a la pagina de registro
    base_page.element.hacer_clic_en_elemento(base_page.home.linkSingIn, "clic_linkSingIn", config.SCREENSHOT_DIR)
    
    # 1. Define la ruta para el archivo JSON de registros
    file_path_json = os.path.join(config.SOURCE_FILES_DIR_DATA_SOURCE, "registros_exitosos.json")
    
    # 2. Recupera los datos del usuario utilizando la función leer_json
    try:
        registros = base_page.file.leer_json(
            json_file_path=file_path_json, 
            nombre_paso="Leer datos de usuario para Login"
        )
        
        # Validación: Asegura que la lista de registros no esté vacía
        if not registros or not isinstance(registros, list):
            base_page.logger.error(f"❌ El archivo JSON no contiene una lista de datos válida en: {file_path_json}")
            # Fallo explícito
            pytest.fail("El archivo de registros de usuarios está vacío o en formato incorrecto.")
            
        # Selecciona un diccionario de usuario al azar de la lista.
        datos_usuario = random.choice(registros)
        
        #Rellenar campos login con datos de usuario existente
        base_page.element.rellenar_campo_de_texto(base_page.signin.txtBoxEmail, datos_usuario["email"], "escribir_campoName", config.SCREENSHOT_DIR)
        base_page.element.rellenar_campo_de_texto(base_page.signin.txtBoxPassword, datos_usuario["password"], "escribir_campoEmail", config.SCREENSHOT_DIR)
        base_page.element.hacer_clic_en_elemento(base_page.signin.btnSignIn, "clic_botonSignup", config.SCREENSHOT_DIR)
        
    except Exception as e:
        base_page.logger.error(f"❌ Error al leer o procesar el archivo JSON: {e}")
        pytest.fail(f"Fallo crítico al cargar datos de credenciales. Error: {e}")
        
def test_signin_con_usuario_no_registrado(set_up_Home: BasePage) -> None:
    """
    [ID: LG-T002] Prueba de Inicio de Sesión con Usuario No Registrado (Credenciales Inválidas).
    
    Verifica que el sistema maneje correctamente los intentos de inicio de sesión 
    con credenciales que no corresponden a un usuario existente, esperando un 
    mensaje de error adecuado.
    
    Pasos:
    1. Iniciar en la página Home (a través del fixture `set_up_Home`).
    2. Hacer clic en el enlace 'Sign In' para ir a la página de inicio de sesión.
    3. Generar datos de usuario aleatorios (email y password) no registrados.
    4. Rellenar los campos de Email y Password con las credenciales generadas.
    5. Hacer clic en el botón 'Sign In'.
    6. Validar que el mensaje de error esperado ('Username/Passoword incorrect') 
       sea visible.
    
    Resultado Esperado:
    La aplicación debe mostrar el mensaje de error de credenciales incorrectas 
    y el usuario debe permanecer en la página de inicio de sesión.
    """
    
    # El fixture `set_up_Home` ya ha realizado la navegación y el manejo de obstáculos.
    # Se asigna la instancia de BasePage a una variable local para mayor claridad.
    base_page = set_up_Home
    
    #Ir a la pagina de registro
    base_page.element.hacer_clic_en_elemento(base_page.home.linkSingIn, "clic_linkSingIn", config.SCREENSHOT_DIR)
    
    # Genera los datos del usuario llamando al método
    # Esto devuelve un diccionario con los datos
    datos_usuario = generador_datos.generar_usuario_valido()
    
    #Rellenar campos registro
    base_page.element.rellenar_campo_de_texto(base_page.signin.txtBoxEmail, datos_usuario["email"], "escribir_campoEmail", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.signin.txtBoxPassword, datos_usuario["password"], "escribir_campoPassword", config.SCREENSHOT_DIR)
    base_page.element.hacer_clic_en_elemento(base_page.signin.btnSignIn, "clic_botonSignup", config.SCREENSHOT_DIR)
    
    #Validar mensaje de error de usuario no registrado
    base_page.element.verificar_texto_contenido(base_page.signin.msgerror, "Username/Passoword incorrect", "verificar_MensajeError", config.SCREENSHOT_DIR)
    # validar que se permanece en la misma pantalla de login
    base_page.navigation.validar_url_actual(config.SIGNIN_URL)
    
def test_signin_con_usuario_con_campos_vacios(set_up_Home: BasePage) -> None:
    """
    [ID: LG-T003] Prueba de Inicio de Sesión con Campos de Entrada Vacíos.
    
    Verifica que la aplicación impida el inicio de sesión cuando el usuario 
    intenta acceder sin proporcionar credenciales (campos Email y Password vacíos),
    y que muestre el mensaje de error de validación requerido.
    
    Pasos:
    1. Iniciar en la página Home (a través del fixture `set_up_Home`).
    2. Hacer clic en el enlace 'Sign In'.
    3. Validar explícitamente que los campos Email y Password estén vacíos.
    4. Intentar hacer clic en el botón 'Sign In'.
    5. Validar que aparece el mensaje de error: "Complete data requiere".
    
    Resultado Esperado:
    El usuario debe permanecer en la URL de Sign In y se debe mostrar 
    el mensaje de error que indica que se requieren datos.
    """
    # El fixture `set_up_Home` ya ha realizado la navegación y el manejo de obstáculos.
    # Se asigna la instancia de BasePage a una variable local para mayor claridad.
    base_page = set_up_Home
    
    #Ir a la pagina de registro
    base_page.element.hacer_clic_en_elemento(base_page.home.linkSingIn, "clic_linkSingIn", config.SCREENSHOT_DIR)
    
    #Validar que los campos email y password está vacíos
    base_page.element.validar_elemento_vacio(base_page.signin.txtBoxEmail, "validar_EmailVacio", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.signin.txtBoxPassword, "validar_PasswordVacio", config.SCREENSHOT_DIR)
    
    #Proceder con login
    base_page.element.hacer_clic_en_elemento(base_page.signin.btnSignIn, "clic_botonSignup", config.SCREENSHOT_DIR)
    
    #Validar mensaje de error de usuario no registrado
    base_page.element.verificar_texto_contenido(base_page.signin.msgerror, "Complete data requiere", "verificar_MensajeError", config.SCREENSHOT_DIR)
    # validar que se permanece en la misma pantalla de login
    base_page.navigation.validar_url_actual(config.SIGNIN_URL)
    
def test_signin_con_usuario_sin_password(set_up_Home: BasePage) -> None:
    """
    [ID: LG-T004] Prueba de Inicio de Sesión: Usuario Válido con Contraseña Vacía.
    
    Verifica que el sistema de login impida el acceso cuando se proporciona 
    un Email válido (de un usuario registrado) pero se deja el campo Password
    vacío. El test valida que se muestre el mensaje de error de validación
    requerido y que el usuario permanezca en la pantalla de login.
    
    Precondición: Se utiliza un usuario existente cargado desde 'registros_exitosos.json'.
    
    Pasos:
    1. Cargar aleatoriamente un usuario existente desde el archivo de registros.
    2. Navegar a la página 'Sign In'.
    3. Rellenar el campo Email con los datos del usuario cargado.
    4. Validar explícitamente que el campo Password está vacío.
    5. Intentar hacer clic en el botón 'Sign In'.
    6. Verificar que el mensaje de error esperado ("Complete data requiere") es visible.
    7. Confirmar que la URL actual sigue siendo la de inicio de sesión.
    """
    # El fixture `set_up_Home` ya ha realizado la navegación y el manejo de obstáculos.
    # Se asigna la instancia de BasePage a una variable local para mayor claridad.
    base_page = set_up_Home
    
    # 1. Define la ruta para el archivo JSON de registros
    file_path_json = os.path.join(config.SOURCE_FILES_DIR_DATA_SOURCE, "registros_exitosos.json")
    
    # 2. Recupera los datos del usuario utilizando la función leer_json
    try:
        registros = base_page.file.leer_json(
            json_file_path=file_path_json, 
            nombre_paso="Leer datos de usuario para Login"
        )
        
        # Validación: Asegura que la lista de registros no esté vacía
        if not registros or not isinstance(registros, list):
            base_page.logger.error(f"❌ El archivo JSON no contiene una lista de datos válida en: {file_path_json}")
            # Fallo explícito
            pytest.fail("El archivo de registros de usuarios está vacío o en formato incorrecto.")
            
        # Selecciona un diccionario de usuario al azar de la lista.
        datos_usuario = random.choice(registros)
    
        #Ir a la pagina de registro
        base_page.element.hacer_clic_en_elemento(base_page.home.linkSingIn, "clic_linkSingIn", config.SCREENSHOT_DIR)
        
        #Rellenar campos login con datos de usuario existente
        base_page.element.rellenar_campo_de_texto(base_page.signin.txtBoxEmail, datos_usuario["email"], "escribir_campoName", config.SCREENSHOT_DIR)
        
        #Validar que el campo password está vacío
        base_page.element.validar_elemento_vacio(base_page.signin.txtBoxPassword, "validar_PasswordVacio", config.SCREENSHOT_DIR)
        
        #Proceder con login
        base_page.element.hacer_clic_en_elemento(base_page.signin.btnSignIn, "clic_botonSignup", config.SCREENSHOT_DIR)
        
        #Validar mensaje de error de usuario no registrado
        base_page.element.verificar_texto_contenido(base_page.signin.msgerror, "Complete data requiere", "verificar_MensajeError", config.SCREENSHOT_DIR)
        # validar que se permanece en la misma pantalla de login
        base_page.navigation.validar_url_actual(config.SIGNIN_URL)
    
    except Exception as e:
        base_page.logger.error(f"❌ Error al leer o procesar el archivo JSON: {e}")
        pytest.fail(f"Fallo crítico al cargar datos de credenciales. Error: {e}")