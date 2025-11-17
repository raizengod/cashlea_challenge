import re
import time
import random
import pytest
import allure
import os
import json
from playwright.sync_api import Page, expect, Playwright, sync_playwright, Locator
from pages.base_page import BasePage 
from utils import config
from typing import Dict, Any, List, Tuple 
from utils.generador_datos import GeneradorDatos

# Crea una instancia del generador de datos
generador_datos = GeneradorDatos()

def test_verificar_elementos_requeridos_presentes_register(set_up_RegisterPage: BasePage) -> None:
    """
    [ID: RE-T001] Verificación de la integridad de la UI de la Página de Registro.

    Objetivo:
        Asegurar que, al navegar a la página de Registro, todos los elementos 
        críticos del formulario (títulos, etiquetas, campos de entrada y botón) 
        estén presentes y visibles, y que el mensaje de feedback (flash message)
        esté oculto por defecto.

    Flujo:
        1. Navegar a la Página de Registro (gestionado por la fixture `set_up_RegisterPage`).
        2. Desplazamiento (Scroll) hasta el título de la página.
        3. Validar el texto del título principal.
        4. Validar el texto de la descripción de la página.
        5. Verificar la visibilidad de las etiquetas y campos de: Username, Password, Confirm Password.
        6. Verificar la visibilidad del botón de Registro.
        7. Verificar que el mensaje de *flash* (éxito/error) no esté visible en el estado inicial.
    
    Parámetros:
        set_up_RegisterPage (BasePage): Fixture que navega a la URL de Registro.
    """
    # La fixture `set_up_RegisterPage` garantiza la navegación exitosa.
    base_page = set_up_RegisterPage
    
    # PASO 1: Desplazamiento hasta el elemento principal de la página.
    base_page.scroll_hasta_elemento(base_page.register.labelRegister, "scroll_HastaLabelRegister", config.SCREENSHOT_DIR)
    
    # PASO 2 y 3: Validar título y descripción de la página.
    base_page.element.verificar_texto_exacto(base_page.register.labelRegister, 
                                            "Test Register page for Automation Testing Practice",
                                            "verificar_textoExactoLabelTitulo", config.SCREENSHOT_DIR)
    
    texto_descripcion_esperado = (
        """Test Register page""")
    base_page.element.verificar_texto_contenido(base_page.register.labelDescriptionRegister, texto_descripcion_esperado,
                                              "verificarTextoDescripciónRegister", base_page.SCREENSHOT_BASE_DIR
                                              )
    
    # PASO 4, 5: Validar visibilidad de todos los elementos del formulario y el botón.
    # Username
    base_page.element.validar_elemento_visible(base_page.register.labelUsernameRegister, "verificarLabelUsernameVisible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.register.txtUsernameRegister, "verificarCampoUsernameVisible", config.SCREENSHOT_DIR)
    # Password
    base_page.element.validar_elemento_visible(base_page.register.labelPasswordRegister, "verificarLabelPasswordVisible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.register.txtPasswordRegister, "verificarCampoPasswordVisible", config.SCREENSHOT_DIR)
    # Confirm Password
    base_page.element.validar_elemento_visible(base_page.register.labelConfirmPasswordRegister, "verificarLabelConfirmPasswordVisible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.register.txtConnfirPasswordRegister, "verificarCampoConfirmPasswordVisible", config.SCREENSHOT_DIR)
    # Botón de Registro
    base_page.element.validar_elemento_visible(base_page.register.btnRegister, "verificarBotónRegisterVisible", config.SCREENSHOT_DIR)
    
    # PASO 6: Validar que el mensaje de feedback (flash message) no está visible inicialmente.
    base_page.element.validar_elemento_no_visible(base_page.register.flashMessage, "verificarMensajeFlashNoVisible", config.SCREENSHOT_DIR)
    
    
def test_registrar_usuario_exitoso(set_up_RegisterPage: BasePage) -> None:
    """
    [ID: RE-T002] Registro exitoso de usuario y persistencia de datos.

    Objetivo:
        Verificar el flujo completo de registro de un nuevo usuario con datos válidos, 
        incluyendo la validación del mensaje de éxito y la persistencia de los datos
        generados en múltiples formatos de archivo (JSON, Excel y CSV) para su 
        uso en pruebas posteriores (ej. inicio de sesión).

    Pasos:
        1. Generar un set de datos de usuario válidos (username, password y confirmar_password).
        2. Rellenar los campos del formulario de Registro.
        3. Hacer clic en el botón 'Register'.
        4. Validar que la aplicación redirige automáticamente a la URL de Login.
        5. Validar que se muestra el mensaje de éxito de registro.
        6. Persistir los datos del usuario registrado en archivos JSON, Excel y CSV.
        
    Args:
        set_up_RegisterPage (BasePage): Fixture que preconfigura el navegador y 
                                        navega a la página de Registro.
    """
    # La fixture `set_up_RegisterPage` asegura la navegación exitosa a la página de Registro.
    base_page = set_up_RegisterPage
    
    # PASO 1: Generar datos de usuario válidos para el registro.
    datos_usuario = generador_datos.generar_usuario_valido()
    
    # PASO 2: Rellenar el formulario de registro con datos válidos.
    base_page.scroll_hasta_elemento(base_page.register.labelUsernameRegister, "scroll_HastaLabelUsername", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.register.txtUsernameRegister, datos_usuario["username"], "escribir_campoUserName", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.register.txtPasswordRegister, datos_usuario["password"], "escribir_campoPassword", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.register.txtConnfirPasswordRegister, datos_usuario["confirmar_password"], "escribir_campoConfirmarPassword", config.SCREENSHOT_DIR)
    
    # PASO 3: Ejecutar la acción de registro.
    base_page.element.hacer_clic_en_elemento(base_page.register.btnRegister, "clic_botonRegister", config.SCREENSHOT_DIR)
    
    # PASO 4: Validar la redirección automática a la URL de Login.
    base_page.navigation.validar_url_actual(config.LOGIN_URL)
    
    # PASO 5: Validar el mensaje de éxito del registro (Flash Message).
    base_page.element.verificar_texto_contenido(base_page.register.flashMessage, 
                                                "Successfully registered, you can log in now.", 
                                                "validar_mensajeRegistroExitoso", config.SCREENSHOT_DIR)
    
    # PASO 6: Persistir los datos del usuario en archivos para su uso posterior (e.g., Login).
    
    # --- Guardar en archivo JSON ---
    file_path_json = os.path.join(config.SOURCE_FILES_DIR_DATA_SOURCE, "registros_exitosos.json")

    # Se usa append=True para añadir los datos al final de una lista en el archivo
    exito_escritura = base_page.file.escribir_json(
        file_path=file_path_json,
        data=datos_usuario,
        append=True,
        nombre_paso="Guardar datos de usuario registrado en JSON"
    )

    if not exito_escritura:
        base_page.logger.error("❌ No se pudieron guardar los datos del usuario en el archivo JSON.")
    
    # --- Guardar en archivo Excel ---
    excel_file_path = os.path.join(config.SOURCE_FILES_DIR_DATA_SOURCE, "registros_exitosos.xlsx")

    # Se pasa una lista con el diccionario. Se usa append=True.
    exito_escritura_excel = base_page.file.escribir_excel(
        file_path=excel_file_path,
        data=[datos_usuario], 
        append=True,
        header=False, # Se asume que los encabezados ya existen si el archivo no es nuevo
        nombre_paso="Guardar datos de usuario registrado en Excel"
    )

    if not exito_escritura_excel:
        base_page.logger.error("❌ No se pudieron guardar los datos del usuario en el archivo Excel.")
    
    # --- Guardar en archivo CSV ---
    file_path_csv = os.path.join(config.SOURCE_FILES_DIR_DATA_SOURCE, 'registros_exitosos.csv')
    
    # Se pasa una lista con el diccionario. Se usa append=True.
    exito_escritura_csv = base_page.file.escribir_csv(
        file_path=file_path_csv,
        data=[datos_usuario], 
        append=True,
        nombre_paso="Guardar datos de usuario registrado en CSV"
    )
    
    if not exito_escritura_csv:
        base_page.logger.error("❌ No se pudieron guardar los datos del usuario en el archivo CSV.")
        
def test_registrar_username_existente(set_up_RegisterPage: BasePage) -> None:
    """
    [ID: RE-T003] Verificación de la no-permisión de registro con Username existente.

    Objetivo:
        Probar la validación de registro al intentar utilizar un 'username' 
        que ya ha sido registrado exitosamente en una prueba anterior. El test
        debe verificar que el sistema rechace el registro, muestre un mensaje 
        de error específico y mantenga al usuario en la página de registro.

    Pasos:
        1. Definir la ruta del archivo JSON de registros.
        2. Leer los datos de usuarios registrados y seleccionar uno al azar.
        3. Generar un par de contraseñas válidas y rellenar el formulario de Registro 
           con el 'username' existente y las nuevas contraseñas.
        4. Hacer clic en el botón 'Register'.
        5. Validar que se muestra el mensaje de error: "Username is being used".
        6. Validar que la URL actual sigue siendo la de Registro.

    Args:
        set_up_RegisterPage (BasePage): Fixture que preconfigura el navegador y 
                                        navega a la página de Registro.
    """
    # La fixture `set_up_RegisterPage` asegura la navegación exitosa a la página de Registro.
    base_page = set_up_RegisterPage
    
    # Se genera un nuevo set de datos válidos solo para usar sus contraseñas frescas.
    datos_usuario_nuevo = generador_datos.generar_usuario_valido()
    
    # PASO 1: Definir la ruta del archivo JSON de registros exitosos.
    file_path_json = os.path.join(config.SOURCE_FILES_DIR_DATA_SOURCE, "registros_exitosos.json")

    # PASO 2: Recuperar y validar los datos de un usuario previamente registrado.
    try:
        registros = base_page.file.leer_json(
            json_file_path=file_path_json, 
            nombre_paso="Leer datos de usuario existente para prueba negativa"
        )
        
        # Validación: Asegura que la lista de registros no esté vacía
        if not registros or not isinstance(registros, list):
            base_page.logger.error(f"\n❌ El archivo JSON no contiene una lista de datos válida en: {file_path_json}")
            # Fallo explícito
            pytest.fail("El archivo de registros de usuarios está vacío o en formato incorrecto. No se puede ejecutar el test.")
            
        # Selecciona un diccionario de usuario al azar de la lista.
        datos_usuario = random.choice(registros)
        
        # PASO 3: Rellenar el formulario de registro con el 'username' existente y contraseñas válidas.
        base_page.scroll_hasta_elemento(base_page.register.labelUsernameRegister, "scroll_HastaLabelUsername", config.SCREENSHOT_DIR)
        
        # Uso del username existente
        base_page.element.rellenar_campo_de_texto(base_page.register.txtUsernameRegister, datos_usuario["username"], "escribir_campoUserNameExistente", config.SCREENSHOT_DIR)
        
        # Uso de contraseñas nuevas y válidas (no relacionadas con el usuario cargado)
        base_page.element.rellenar_campo_de_texto(base_page.register.txtPasswordRegister, datos_usuario_nuevo["password"], "escribir_campoPassword", config.SCREENSHOT_DIR)
        base_page.element.rellenar_campo_de_texto(base_page.register.txtConnfirPasswordRegister, datos_usuario_nuevo["confirmar_password"], "escribir_campoConfirmarPassword", config.SCREENSHOT_DIR)
        
        # PASO 4: Ejecutar la acción de registro.
        base_page.element.hacer_clic_en_elemento(base_page.register.btnRegister, "clic_botonRegister", config.SCREENSHOT_DIR)
        
        # PASO 5: Validar el mensaje de error de usuario ya registrado.
        base_page.element.verificar_texto_contenido(base_page.register.flashMessage, "Username is being used", "verificar_MensajeErrorUsernameExistente", config.SCREENSHOT_DIR)
        
        # PASO 6: Validar que el usuario permanece en la misma pantalla de registro (no hay redirección).
        base_page.navigation.validar_url_actual(config.REGISTER_URL)
        
    except Exception as e:
        base_page.logger.error(f"❌ Error crítico al leer datos o ejecutar el test: {e}")
        pytest.fail(f"\nFallo crítico en el test de username existente. Error: {e}")
        
def test_registrar_usurio_con_campos_vacios(set_up_RegisterPage: BasePage) -> None:
    """
    [ID: RE-T004] Verificación de la validación de campos vacíos en el formulario de Registro.

    Objetivo:
        Probar que el sistema impide el registro cuando todos los campos 
        obligatorios (Username, Password, Confirm Password) se dejan vacíos. 
        El test debe validar que se muestra el mensaje de error de 'campos requeridos' 
        y que el usuario permanece en la página de Registro.

    Pasos:
        1. Validar que los campos de Username, Password y Confirm Password están inicialmente vacíos.
        2. Hacer clic en el botón 'Register' sin rellenar ningún campo.
        3. Validar que se muestra el mensaje de error: "All fields are required.".
        4. Validar que la URL actual sigue siendo la de Registro (no hay redirección).

    Args:
        set_up_RegisterPage (BasePage): Fixture que preconfigura el navegador y 
                                        navega a la página de Registro.
    """
    # La fixture `set_up_RegisterPage` asegura la navegación exitosa a la página de Registro.
    base_page = set_up_RegisterPage
    
    # PASO 1: Validar que los campos están inicialmente vacíos (pre-condición).
    base_page.scroll_hasta_elemento(base_page.register.labelUsernameRegister, "scroll_HastaLabelUsername", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.register.txtUsernameRegister, "validar_UsernameVacio", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.register.txtPasswordRegister, "validar_PasswordVacio", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.register.txtConnfirPasswordRegister, "validar_ConfirmVacio", config.SCREENSHOT_DIR)
    
    # PASO 2: Proceder con registro sin rellenar los campos.
    base_page.element.hacer_clic_en_elemento(base_page.register.btnRegister, "click_botonRegisterCamposVacios", config.SCREENSHOT_DIR)
    
    # PASO 3: Validar mensaje de error de campos requeridos.
    base_page.element.verificar_texto_contenido(base_page.register.flashMessage, "All fields are required.", "verificar_MensajeErrorCamposVacios", config.SCREENSHOT_DIR)
    
    # PASO 4: Validar que se permanece en la misma pantalla de registro.
    base_page.navigation.validar_url_actual(config.REGISTER_URL)
    
def test_registrar_usurio_con_solo_username(set_up_RegisterPage: BasePage) -> None:
    """
    [ID: RE-T005] Verificación de la validación de campos requeridos (Password y Confirm Password).

    Objetivo:
        Probar que el sistema impide el registro cuando solo se rellena el campo 
        Username, dejando vacíos los campos obligatorios de contraseña. Además, 
        se verifica que el valor introducido en el campo Username se conserve en el formulario.

    Pasos:
        1. Generar un set de datos de usuario válidos (solo se usará el username).
        2. Rellenar únicamente el campo Username.
        3. Validar que los campos Password y Confirm Password están vacíos.
        4. Hacer clic en el botón 'Register'.
        5. Validar que el valor introducido en Username se ha conservado en el campo.
        6. Validar que se muestra el mensaje de error: "All fields are required.".
        7. Validar que la URL actual sigue siendo la de Registro (no hay redirección).

    Args:
        set_up_RegisterPage (BasePage): Fixture que preconfigura el navegador y 
                                        navega a la página de Registro.
    """
    # La fixture `set_up_RegisterPage` asegura la navegación exitosa a la página de Registro.
    base_page = set_up_RegisterPage
    
    # PASO 1: Generar un set de datos de usuario válidos (solo se usará el username).
    datos_usuario = generador_datos.generar_usuario_valido()
    
    # PASO 2: Rellenar únicamente el campo Username.
    base_page.scroll_hasta_elemento(base_page.register.labelUsernameRegister, "scroll_HastaLabelUsername", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.register.txtUsernameRegister, datos_usuario["username"], "escribir_campoUserName", config.SCREENSHOT_DIR)
        
    # PASO 3: Validar que los campos Password y Confirm Password están vacíos (pre-condición/verificación).
    base_page.element.validar_elemento_vacio(base_page.register.txtPasswordRegister, "validar_PasswordVacio", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.register.txtConnfirPasswordRegister, "validar_ConfirmPasswordVacio", config.SCREENSHOT_DIR)
    
    # PASO 4: Proceder con registro.
    base_page.element.hacer_clic_en_elemento(base_page.register.btnRegister, "click_botonRegisterSoloUsername", config.SCREENSHOT_DIR)
    
    # PASO 5: Validar que el valor introducido en Username se ha conservado.
    base_page.element.verificar_valor_campo(base_page.register.txtUsernameRegister, datos_usuario["username"], "verificarUsenameConserveDato", config.SCREENSHOT_DIR)
    
    # PASO 6: Validar mensaje de error de campos requeridos.
    base_page.element.verificar_texto_contenido(base_page.register.flashMessage, "All fields are required.", "verificar_MensajeErrorCamposVacios", config.SCREENSHOT_DIR)
    
    # PASO 7: Validar que se permanece en la misma pantalla de registro.
    base_page.navigation.validar_url_actual(config.REGISTER_URL)
    
def test_registrar_usuario_sin_confirm_password(set_up_RegisterPage: BasePage) -> None:
    """
    [ID: RE-T006] Verificación de la validación de campo requerido (Confirm Password).

    Objetivo:
        Probar que el sistema impide el registro cuando se rellenan el Username y el Password, 
        pero se deja vacío el campo Confirm Password. Se debe verificar que se muestre el 
        mensaje de error de 'campos requeridos' y que los valores introducidos en Username 
        y Password se conserven en el formulario.

    Pasos:
        1. Generar un set de datos de usuario válidos (solo se usarán Username y Password).
        2. Rellenar los campos Username y Password.
        3. Validar que el campo Confirm Password está vacío.
        4. Hacer clic en el botón 'Register'.
        5. Validar que se muestra el mensaje de error: "All fields are required.".
        6. Validar que los valores introducidos en Username y Password se han conservado.
        7. Validar que el campo Confirm Password sigue vacío.
        8. Validar que la URL actual sigue siendo la de Registro (no hay redirección).

    Args:
        set_up_RegisterPage (BasePage): Fixture que preconfigura el navegador y 
                                        navega a la página de Registro.
    """
    # La fixture `set_up_RegisterPage` asegura la navegación exitosa a la página de Registro.
    base_page = set_up_RegisterPage
    
    # PASO 1: Generar un set de datos de usuario válidos (solo se usarán Username y Password).
    datos_usuario = generador_datos.generar_usuario_valido()
    
    # PASO 2: Rellenar los campos Username y Password.
    base_page.scroll_hasta_elemento(base_page.register.labelUsernameRegister, "scroll_HastaLabelUsername", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.register.txtUsernameRegister, datos_usuario["username"], "escribir_campoUserName", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.register.txtPasswordRegister, datos_usuario["password"], "escribir_campoPassword", config.SCREENSHOT_DIR)
        
    # PASO 3: Validar que el campo Confirm Password está vacío (pre-condición/verificación).
    base_page.element.validar_elemento_vacio(base_page.register.txtConnfirPasswordRegister, "validar_ConfirmPasswordVacioAntesClick", config.SCREENSHOT_DIR)
    
    # PASO 4: Proceder con registro.
    base_page.element.hacer_clic_en_elemento(base_page.register.btnRegister, "click_botonRegisterSinConfirm", config.SCREENSHOT_DIR)
    
    # PASO 5: Validar mensaje de error de campos requeridos.
    base_page.element.verificar_texto_contenido(base_page.register.flashMessage, "All fields are required.", "verificar_MensajeErrorCamposVacios", config.SCREENSHOT_DIR)
    
    # PASO 6: Validar que los valores introducidos en Username y Password se han conservado.
    base_page.scroll_hasta_elemento(base_page.register.labelUsernameRegister, "scroll_HastaLabelUsernameDespuesClick", config.SCREENSHOT_DIR)
    base_page.element.verificar_valor_campo(base_page.register.txtUsernameRegister, datos_usuario["username"], "verificarUsenameConserveDato", config.SCREENSHOT_DIR)
    # NOTA: En muchos sistemas, la contraseña se borra después de un intento fallido o por diseño de seguridad. 
    # Aquí validamos si el campo de Password se ha vaciado o no, asumiendo que el campo de Password NO conserva el valor (es la práctica más segura).
    base_page.element.validar_elemento_vacio(base_page.register.txtPasswordRegister, "validar_PasswordSeVació", config.SCREENSHOT_DIR)
    
    # PASO 7: Validar que el campo Confirm Password sigue vacío.
    base_page.element.validar_elemento_vacio(base_page.register.txtConnfirPasswordRegister, "validar_ConfirmVacioFinal", config.SCREENSHOT_DIR)
    
    # PASO 8: Validar que se permanece en la misma pantalla de registro.
    base_page.navigation.validar_url_actual(config.REGISTER_URL)
    
def test_registrar_usuario_con_password_y_confirm_password_diferentes(set_up_RegisterPage: BasePage) -> None:
    """
    [ID: RE-T007] Prueba de Control de Errores: Registro con Contraseñas No Coincidentes.

    Objetivo:
        Verificar que el sistema impide el registro cuando los campos 'Password' y
        'Confirm Password' no contienen el mismo valor, y valida que el mensaje
        de error correspondiente se muestre correctamente.

    Flujo:
        1. Generar un set de datos de usuario válido.
        2. Generar una segunda contraseña 'diferente' para el campo de confirmación.
        3. Rellenar 'Username' y 'Password' con datos válidos.
        4. Rellenar 'Confirm Password' con la contraseña 'diferenteConfirmacion'.
        5. Intentar hacer clic en el botón de Registro.
        6. **Validación:** Verificar que el mensaje de error "Passwords do not match." es visible.
        7. **Validación:** Verificar que la URL no cambia, confirmando que el usuario permanece en la página de registro.

    Parámetros:
        set_up_RegisterPage (BasePage): Fixture que navega a la página de Registro.
    """
    # El fixture `set_up_RegisterPage` asegura la navegación exitosa a la página de Registro.
    base_page = set_up_RegisterPage
    
    # PASO 1: Generar un set de datos de usuario válidos y una contraseña diferente.
    datos_usuario = generador_datos.generar_usuario_valido()
    # Se genera una contraseña fuerte, pero garantizando que sea distinta a la principal.
    diferenteConfirmacion = generador_datos.generar_password_segura()
    
    # PASO 2: Rellenar los campos Username, Password y Confirm Password (con el valor diferente).
    base_page.scroll_hasta_elemento(base_page.register.labelUsernameRegister, "scroll_HastaLabelUsername", config.SCREENSHOT_DIR)
    # Rellenar campo 'Username'
    base_page.element.rellenar_campo_de_texto(base_page.register.txtUsernameRegister, datos_usuario["username"], "escribir_campoUserName", config.SCREENSHOT_DIR)
    # Rellenar campo 'Password'
    base_page.element.rellenar_campo_de_texto(base_page.register.txtPasswordRegister, datos_usuario["password"], "escribir_campoPassword", config.SCREENSHOT_DIR)
    # Rellenar campo 'Confirm Password' con una contraseña diferente
    base_page.element.rellenar_campo_de_texto(base_page.register.txtConnfirPasswordRegister, diferenteConfirmacion, "escribir_campoConfirmPasswordDiferente", config.SCREENSHOT_DIR)
    
    # PASO 3: Proceder con registro.
    base_page.element.hacer_clic_en_elemento(base_page.register.btnRegister, "click_botonRegisterConContrasenasDiferentes", config.SCREENSHOT_DIR)
    
    # PASO 4: Validar mensaje de error de que las contraseñas no coinciden.
    base_page.element.verificar_texto_contenido(base_page.register.flashMessage, "Passwords do not match.", "verificar_MensajeErrorPasswordDirefrentes", config.SCREENSHOT_DIR)
    
    # PASO 5: Validar que se permanece en la misma pantalla de registro.
    base_page.navigation.validar_url_actual(config.REGISTER_URL)
    
def test_cerrar_mensaje_flash(set_up_RegisterPage: BasePage) -> None:
    """
    [ID: RE-T008] Verificación de la funcionalidad de cerrar el Mensaje Flash de Error.

    Objetivo:
        Probar la capacidad del usuario para descartar o cerrar un mensaje de 
        error o notificación (Flash Message) una vez que ha aparecido, validando 
        que el elemento ya no sea visible en la interfaz después de la interacción.

    Pasos:
        1. Validar que el formulario de Registro está vacío.
        2. Intentar registrarse sin rellenar ningún campo para provocar la aparición del Flash Message.
        3. Validar que la URL se mantiene en la página de Registro.
        4. Validar que el Flash Message (mensaje de error) es visible.
        5. Hacer clic en el botón de cerrar ('X') del Flash Message.
        6. Validar que el Flash Message ya no es visible en la interfaz.

    Args:
        set_up_RegisterPage (BasePage): Fixture que preconfigura el navegador y 
                                        navega a la página de Registro.
    """
    # La fixture `set_up_RegisterPage` asegura la navegación exitosa a la página de Registro.
    base_page = set_up_RegisterPage
    
    base_page.scroll_hasta_elemento(base_page.register.labelUsernameRegister, "scroll_HastaLabelUsername", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.register.txtUsernameRegister, "validar_UsernameVacio", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.register.txtPasswordRegister, "validar_PasswordVacio", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.register.txtConnfirPasswordRegister, "validar_ConfirmVacio", config.SCREENSHOT_DIR)
    
    base_page.element.hacer_clic_en_elemento(base_page.register.btnRegister, "click_botonRegisterCamposVacios", config.SCREENSHOT_DIR)
    
    base_page.navigation.validar_url_actual(config.REGISTER_URL)
    
    base_page.element.validar_elemento_visible(base_page.register.flashMessage, "verificar_MensajeFlashVisible", config.SCREENSHOT_DIR)
    
    base_page.element.hacer_clic_en_elemento(base_page.register.btnCerrarFlashMessage, "clic_CerrarMensajeFlash", config.SCREENSHOT_DIR)
    
    base_page.element.validar_elemento_no_visible(base_page.register.flashMessage, "verificar_MensajeFlashNoVisible", config.SCREENSHOT_DIR)
    
    