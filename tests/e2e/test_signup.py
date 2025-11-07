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

def test_registrar_usuario_exitoso(set_up_Home: BasePage) -> None:
    """
    [ID: RE-T001] Flujo E2E: Registro de Usuario, Persistencia de Datos

    Este test verifica el ciclo completo de vida de un usuario en la aplicación 'Home — Conduit':
    1. Navega a la página de inicio.
    2. Genera datos de usuario únicos y aleatorios.
    3. Completa el formulario de registro inicial y el formulario de detalles completos.
    4. Persiste los datos del usuario generado en archivos JSON, Excel (.xlsx) y CSV.

    :param base_page: Fixture que proporciona la instancia de 'BasePage' con acceso a todas
                      las acciones de navegación, elementos, manejo de archivos y logging.
    :type base_page: BasePage
    :return: None
    """
    # El fixture `set_up_Home` ya ha realizado la navegación y el manejo de obstáculos.
    # Se asigna la instancia de BasePage a una variable local para mayor claridad.
    base_page = set_up_Home
    
    #Ir a la pagina de registro
    base_page.element.hacer_clic_en_elemento(base_page.home.linkSingUp, "clic_linkSingUp", config.SCREENSHOT_DIR)
    #Verificando que el label New User Signup! sea visible
    base_page.element.validar_elemento_visible(base_page.signup.labelSingUp, "validar_labelSingUp_visible", config.SCREENSHOT_DIR)
    
    # Genera los datos del usuario llamando al método
    # Esto devuelve un diccionario con los datos
    datos_usuario = generador_datos.generar_usuario_valido()
    
    #Rellenar campos registro
    base_page.element.rellenar_campo_de_texto(base_page.signup.txtBoxUserName, datos_usuario["username"], "escribir_campoUserName", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.signup.txtBoxEmail, datos_usuario["email"], "escribir_campoEmail", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.signup.txtBoxPassword, datos_usuario["password"], "escribir_campoPassword", config.SCREENSHOT_DIR)
    base_page.element.hacer_clic_en_elemento(base_page.signup.btnSignUp, "clic_botonSignup", config.SCREENSHOT_DIR)
    
    """# Valida que se muestre un mensaje de usuario registrado exitomsamente.
    base_page.element.verificar_texto_contenido(base_page.register.mensajeCuentaCreada, "Congratulations! Your new account has been successfully created!", "validar_mensajeRegistroExitoso", config.SCREENSHOT_DIR)"""
    
    # Guarda los datos del usuario registrado en un archivo JSON
    # Define la ruta para el archivo JSON de registros
    file_path_json = os.path.join(config.SOURCE_FILES_DIR_DATA_SOURCE, "registros_exitosos.json")

    # Se usa append=True para añadir los datos al final de una lista en el archivo
    exito_escritura = base_page.file.escribir_json(
        file_path=file_path_json,
        data=datos_usuario,
        append=True,
        nombre_paso="Guardar datos de usuario registrado"
    )

    if not exito_escritura:
        base_page.logger.error("❌ No se pudieron guardar los datos del usuario en el archivo JSON.")
    
    # Guarda los datos del usuario registrado en un archivo Excel
    # Define la ruta para el archivo Excel de registros
    excel_file_path = os.path.join(config.SOURCE_FILES_DIR_DATA_SOURCE, "registros_exitosos.xlsx")

    # Llama a la función escribir_excel para guardar los datos en modo 'append'
    exito_escritura_excel = base_page.file.escribir_excel(
        file_path=excel_file_path,
        data=[datos_usuario], # Se pasa una lista con el diccionario
        append=True,
        header=False, # Se asegura que no se escriban los encabezados si es un archivo nuevo
        nombre_paso="Guardar datos de usuario registrado en Excel"
    )

    if not exito_escritura_excel:
        base_page.logger.error("❌ No se pudieron guardar los datos del usuario en el archivo Excel.")    
    
    # Guarda los datos del usuario registrado en un archivo CSV
    # Define la ruta para el archivo CSV de registros
    file_path_csv = os.path.join(config.SOURCE_FILES_DIR_DATA_SOURCE, 'registros_exitosos.csv')
    
    # Llama a la función escribir_excel para guardar los datos en modo 'append'
    exito_escritura_csv = base_page.file.escribir_csv(
        file_path=file_path_csv,
        data=[datos_usuario], # Se pasa una lista con el diccionario
        append=True,
        nombre_paso="Guardar datos de usuario registrado en CSV_con_encabezado"
    )
    
    if not exito_escritura_csv:
        base_page.logger.error("❌ No se pudieron guardar los datos del usuario en el archivo CSV.")
        
def test_registrar_username_existente(set_up_Home: BasePage) -> None:
    """
    [ID: RE-T002] Flujo E2E: Registro de username registrado previamente

    Este test verifica el ciclo completo de vida de un usuario en la aplicación 'Home — Conduit':
    1. Navega a la página de inicio.
    2. Usar datos de usuario únicos usados previamente.
    3. Completa el formulario de registro inicial y el formulario de detalles completos.

    :param base_page: Fixture que proporciona la instancia de 'BasePage' con acceso a todas
                      las acciones de navegación, elementos, manejo de archivos y logging.
    :type base_page: BasePage
    :return: None
    """
    # El fixture `set_up_Home` ya ha realizado la navegación y el manejo de obstáculos.
    # Se asigna la instancia de BasePage a una variable local para mayor claridad.
    base_page = set_up_Home
    
    #Ir a la pagina de registro
    base_page.element.hacer_clic_en_elemento(base_page.home.linkSingUp, "clic_linkSingUp", config.SCREENSHOT_DIR)
    #Verificando que el label New User Signup! sea visible
    base_page.element.validar_elemento_visible(base_page.signup.labelSingUp, "validar_labelSingUp_visible", config.SCREENSHOT_DIR)
    
    # Genera los datos del usuario llamando al método
    # Esto devuelve un diccionario con los datos
    datos_usuario_nuevo = generador_datos.generar_usuario_valido()
    
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
        
        #Rellenar campos registro con datos de usuario existente
        base_page.element.rellenar_campo_de_texto(base_page.signup.txtBoxUserName, datos_usuario["username"], "escribir_campoUserName", config.SCREENSHOT_DIR)
        base_page.element.rellenar_campo_de_texto(base_page.signup.txtBoxEmail, datos_usuario_nuevo["email"], "escribir_campoName", config.SCREENSHOT_DIR)
        base_page.element.rellenar_campo_de_texto(base_page.signup.txtBoxPassword, datos_usuario_nuevo["password"], "escribir_campoEmail", config.SCREENSHOT_DIR)
        base_page.element.hacer_clic_en_elemento(base_page.signup.btnSignUp, "clic_botonSignup", config.SCREENSHOT_DIR)
        
        #Validar mensaje de error de usuario registrado previamente
        base_page.element.verificar_texto_contenido(base_page.signup.msgerror, "Username is being used", "verificar_MensajeError", config.SCREENSHOT_DIR)
        # validar que se permanece en la misma pantalla de registro
        base_page.navigation.validar_url_actual(config.SIGNUP_URL)
        
    except Exception as e:
        base_page.logger.error(f"❌ Error al leer o procesar el archivo JSON: {e}")
        pytest.fail(f"\nFallo crítico al cargar datos de credenciales. Error: {e}")
        
def test_registrar_email_existente(set_up_Home: BasePage) -> None:
    """
    [ID: RE-T003] Flujo E2E: Registro de email registrado previamente

    Este test verifica el ciclo completo de vida de un usuario en la aplicación 'Home — Conduit':
    1. Navega a la página de inicio.
    2. Usar datos de usuario únicos usados previamente.
    3. Completa el formulario de registro inicial y el formulario de detalles completos.

    :param base_page: Fixture que proporciona la instancia de 'BasePage' con acceso a todas
                      las acciones de navegación, elementos, manejo de archivos y logging.
    :type base_page: BasePage
    :return: None
    """
    # El fixture `set_up_Home` ya ha realizado la navegación y el manejo de obstáculos.
    # Se asigna la instancia de BasePage a una variable local para mayor claridad.
    base_page = set_up_Home
    
    #Ir a la pagina de registro
    base_page.element.hacer_clic_en_elemento(base_page.home.linkSingUp, "clic_linkSingUp", config.SCREENSHOT_DIR)
    #Verificando que el label New User Signup! sea visible
    base_page.element.validar_elemento_visible(base_page.signup.labelSingUp, "validar_labelSingUp_visible", config.SCREENSHOT_DIR)
    
    # Genera los datos del usuario llamando al método
    # Esto devuelve un diccionario con los datos
    datos_usuario_nuevo = generador_datos.generar_usuario_valido()
    
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
        
        #Rellenar campos registro con datos de usuario existente
        base_page.element.rellenar_campo_de_texto(base_page.signup.txtBoxUserName, datos_usuario_nuevo["username"], "escribir_campoUserName", config.SCREENSHOT_DIR)
        base_page.element.rellenar_campo_de_texto(base_page.signup.txtBoxEmail, datos_usuario["email"], "escribir_campoName", config.SCREENSHOT_DIR)
        base_page.element.rellenar_campo_de_texto(base_page.signup.txtBoxPassword, datos_usuario_nuevo["password"], "escribir_campoEmail", config.SCREENSHOT_DIR)
        base_page.element.hacer_clic_en_elemento(base_page.signup.btnSignUp, "clic_botonSignup", config.SCREENSHOT_DIR)
        
        #Validar mensaje de error de usuario registrado previamente
        base_page.element.verificar_texto_contenido(base_page.signup.msgerror, "Email is being used", "verificar_MensajeError", config.SCREENSHOT_DIR)
        # validar que se permanece en la misma pantalla de registro
        base_page.navigation.validar_url_actual(config.SIGNUP_URL)
        
    except Exception as e:
        base_page.logger.error(f"❌ Error al leer o procesar el archivo JSON: {e}")
        pytest.fail(f"\nFallo crítico al cargar datos de credenciales. Error: {e}")
        
def test_registrar_usurio_con_campos_vacios(set_up_Home: BasePage) -> None:
    """
    [ID: RE-T004] Prueba de Registro: Campos de Formulario Completamente Vacíos.

    Verifica que el sistema de registro (Sign Up) impida la creación de un nuevo
    usuario cuando todos los campos obligatorios (Username, Email y Password) se 
    dejan completamente vacíos.

    Pasos:
    1. Navegar a la página 'Sign Up' y validar que el formulario está visible.
    2. Confirmar que los campos Username, Email y Password están vacíos.
    3. Intentar hacer clic en el botón 'Sign Up'.
    4. Verificar que el mensaje de error esperado ("Complete data requiere") es visible.
    5. Confirmar que se permanece en la URL de registro.
    """
    # El fixture `set_up_Home` ya ha realizado la navegación y el manejo de obstáculos.
    # Se asigna la instancia de BasePage a una variable local para mayor claridad.
    base_page = set_up_Home
    
    #Ir a la pagina de registro
    base_page.element.hacer_clic_en_elemento(base_page.home.linkSingUp, "clic_linkSingUp", config.SCREENSHOT_DIR)
    #Verificando que el label New User Signup! sea visible
    base_page.element.validar_elemento_visible(base_page.signup.labelSingUp, "validar_labelSingUp_visible", config.SCREENSHOT_DIR)
    
    #Validar que los campos username, email y password está vacíos
    base_page.element.validar_elemento_vacio(base_page.signup.txtBoxUserName, "validar_UsernameVacio", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.signup.txtBoxEmail, "validar_EmailVacio", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.signup.txtBoxPassword, "validar_PasswordVacio", config.SCREENSHOT_DIR)
    
    #Proceder con registro
    base_page.element.hacer_clic_en_elemento(base_page.signup.btnSignUp, "click_botónSignUp", config.SCREENSHOT_DIR)
    
    #Validar mensaje de error de usuario registrado previamente
    base_page.element.verificar_texto_contenido(base_page.signup.msgerror, "Complete data requiere", "verificar_MensajeError", config.SCREENSHOT_DIR)
    # validar que se permanece en la misma pantalla de registro
    base_page.navigation.validar_url_actual(config.SIGNUP_URL)
    
def test_registrar_usurio_con_solo_username(set_up_Home: BasePage) -> None:
    """
    [ID: RE-T005] Prueba de Registro: Solo se Proporciona el Nombre de Usuario (Username).

    Valida que el sistema de registro requiere la entrada de Email y Password,
    impidiendo el registro cuando solo se proporciona el campo Username.

    Pasos:
    1. Generar datos válidos de usuario.
    2. Navegar a la página 'Sign Up'.
    3. Rellenar únicamente el campo Username.
    4. Confirmar que los campos Email y Password están vacíos.
    5. Intentar hacer clic en el botón 'Sign Up'.
    6. Verificar que el mensaje de error esperado ("Compplete the data requiere") es visible.
    7. Confirmar que se permanece en la URL de registro.
    """
    # El fixture `set_up_Home` ya ha realizado la navegación y el manejo de obstáculos.
    # Se asigna la instancia de BasePage a una variable local para mayor claridad.
    base_page = set_up_Home
    
    # Genera los datos del usuario llamando al método
    # Esto devuelve un diccionario con los datos
    datos_usuario = generador_datos.generar_usuario_valido()
    
    #Ir a la pagina de registro
    base_page.element.hacer_clic_en_elemento(base_page.home.linkSingUp, "clic_linkSingUp", config.SCREENSHOT_DIR)
    #Verificando que el label New User Signup! sea visible
    base_page.element.validar_elemento_visible(base_page.signup.labelSingUp, "validar_labelSingUp_visible", config.SCREENSHOT_DIR)
    
    #Rellenar campos registro con datos de usuario existente
    base_page.element.rellenar_campo_de_texto(base_page.signup.txtBoxUserName, datos_usuario["username"], "escribir_campoUserName", config.SCREENSHOT_DIR)
        
    #Validar que los campos email y password está vacíos
    base_page.element.validar_elemento_vacio(base_page.signup.txtBoxEmail, "validar_EmailVacio", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.signup.txtBoxPassword, "validar_PasswordVacio", config.SCREENSHOT_DIR)
    
    #Proceder con registro
    base_page.element.hacer_clic_en_elemento(base_page.signup.btnSignUp, "click_botónSignUp", config.SCREENSHOT_DIR)
    
    #Validar mensaje de error de usuario registrado previamente
    base_page.element.verificar_texto_contenido(base_page.signup.msgerror, "Compplete the data requiere", "verificar_MensajeError", config.SCREENSHOT_DIR)
    # validar que se permanece en la misma pantalla de registro
    base_page.navigation.validar_url_actual(config.SIGNUP_URL)
    
def test_registrar_usurio_sin_password(set_up_Home: BasePage) -> None:
    """
    [ID: RE-T006] Prueba de Registro: Falta la Contraseña (Password) Obligatoria.

    Comprueba que el flujo de registro falle cuando se proporcionan el Username y el Email, 
    pero se omite la Contraseña (Password), validando el requisito de datos completos.

    Pasos:
    1. Generar un conjunto de datos válidos (Username, Email, Password).
    2. Navegar a la página 'Sign Up'.
    3. Rellenar los campos Username y Email.
    4. Confirmar que el campo Password está vacío.
    5. Intentar hacer clic en el botón 'Sign Up'.
    6. Verificar que el mensaje de error esperado ("Compplete the data requiere") es visible.
    7. Confirmar que se permanece en la URL de registro.
    """
    # El fixture `set_up_Home` ya ha realizado la navegación y el manejo de obstáculos.
    # Se asigna la instancia de BasePage a una variable local para mayor claridad.
    base_page = set_up_Home
    
    # Genera los datos del usuario llamando al método
    # Esto devuelve un diccionario con los datos
    datos_usuario = generador_datos.generar_usuario_valido()
    
    #Ir a la pagina de registro
    base_page.element.hacer_clic_en_elemento(base_page.home.linkSingUp, "clic_linkSingUp", config.SCREENSHOT_DIR)
    #Verificando que el label New User Signup! sea visible
    base_page.element.validar_elemento_visible(base_page.signup.labelSingUp, "validar_labelSingUp_visible", config.SCREENSHOT_DIR)
    
    #Rellenar campos registro con datos de usuario existente
    base_page.element.rellenar_campo_de_texto(base_page.signup.txtBoxUserName, datos_usuario["username"], "escribir_campoUserName", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.signup.txtBoxEmail, datos_usuario["email"], "escribir_campoUserName", config.SCREENSHOT_DIR)
        
    #Validar que los campos email y password está vacíos
    base_page.element.validar_elemento_vacio(base_page.signup.txtBoxPassword, "validar_PasswordVacio", config.SCREENSHOT_DIR)
    
    #Proceder con registro
    base_page.element.hacer_clic_en_elemento(base_page.signup.btnSignUp, "click_botónSignUp", config.SCREENSHOT_DIR)
    
    #Validar mensaje de error de usuario registrado previamente
    base_page.element.verificar_texto_contenido(base_page.signup.msgerror, "Compplete the data requiere", "verificar_MensajeError", config.SCREENSHOT_DIR)
    # validar que se permanece en la misma pantalla de registro
    base_page.navigation.validar_url_actual(config.SIGNUP_URL)