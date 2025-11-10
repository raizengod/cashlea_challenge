import re
import time
import random
import pytest
import os
import json
from playwright.sync_api import Page, expect, Playwright, sync_playwright
from pages.base_page import BasePage
from utils import config

def test_verificar_opciones_a_probar_visible(set_up_Home: BasePage) -> None:
    """
    [ID: HM-T001] Prueba la visibilidad de los enlaces de las funcionalidades principales
    en la página de inicio del sitio de práctica.

    Este test verifica que las opciones clave de navegación estén presentes y visibles
    para el usuario después de cargar la página principal.

    Flujo:
    1. Scroll hacia abajo hasta la ubicación de los enlaces de las funcionalidades.
    2. Valida que los siguientes elementos sean visibles en la UI:
        - 'Web Input Examples' (linkWebInput)
        - 'Test Login' (linkTestLogin)
        - 'Test Register' (linkTestRegister)
        - 'Dynamic Table' (linkDynamicTable)

    Parámetros:
        set_up_Home (BasePage): Fixture que inicializa el navegador, navega a la URL
                                 base y devuelve la instancia de la Page Object Model.

    Retorna:
        None: La prueba pasa si todos los enlaces son visibles; falla en caso contrario.
    """
    # El fixture `set_up_Home` ya ha realizado la navegación y el manejo de obstáculos.
    # Se asigna la instancia de BasePage a una variable local para mayor claridad.
    base_page = set_up_Home
    
    base_page.scroll_hasta_elemento(base_page.home.linkWebInput, "scroll_HastaWebInput", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.home.linkWebInput, "validadVisibilidad_WebInput", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.home.linkTestLogin, "validadVisibilidad_TestLogin", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.home.linkTestRegister, "validadVisibilidad_TestRegister", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.home.linkDynamicTable, "validadVisibilidad_DynamicTable", config.SCREENSHOT_DIR)
    
def test_ingresar_Web_input_y_regresar_a_home(set_up_Home: BasePage) -> None:
    """
    [ID: HM-T002] Prueba la navegación de ida y vuelta entre la página de inicio
    y la sección 'Web Input Examples'.

    Este test verifica que el usuario pueda acceder correctamente a una funcionalidad
    desde el home y luego regresar a la página principal utilizando la navegación
    del navegador (función 'volver').

    Flujo:
    1. Scroll hasta el enlace 'Web Input Examples'.
    2. Hace clic en el enlace 'Web Input Examples'.
    3. **Validación (Ida):** Verifica que la URL actual sea la de 'Web Input Examples'.
    4. Utiliza la función de navegación para volver a la página anterior.
    5. **Validación (Regreso):** Verifica que la URL actual sea nuevamente la URL base (Home).

    Parámetros:
        set_up_Home (BasePage): Fixture que inicializa el navegador y navega a la URL base.

    Retorna:
        None: La prueba pasa si las validaciones de URL confirman la navegación correcta.
    """
    
    # El fixture `set_up_Home` ya ha realizado la navegación y el manejo de obstáculos.
    # Se asigna la instancia de BasePage a una variable local para mayor claridad.
    base_page = set_up_Home
    
    base_page.scroll_hasta_elemento(base_page.home.linkWebInput, "scroll_HastaWebInput", config.SCREENSHOT_DIR)
    
    base_page.element.hacer_clic_en_elemento(base_page.home.linkWebInput, "clic_ingresarAWebInput", config.SCREENSHOT_DIR)
    
    base_page.navigation.validar_url_actual(config.WEBINPUT_URL)
    
    base_page.navigation.volver_a_pagina_anterior("regrserAHome", config.SCREENSHOT_DIR)
    
    base_page.navigation.validar_url_actual(config.BASE_URL)
    
def test_ingresar_login_y_regresar_a_home(set_up_Home: BasePage) -> None:
    """
    [ID: HM-T003] Prueba la navegación de ida y vuelta entre la página de inicio
    y la sección 'Test Login'.

    Este test verifica que el usuario pueda acceder correctamente a la página de
    inicio de sesión desde el home y que el botón de retroceso (navegación anterior)
    funcione para retornar a la página principal.

    Flujo:
    1. Scroll hasta el enlace 'Test Login' en la página principal.
    2. Hace clic en el enlace 'Test Login'.
    3. **Validación (Ida):** Verifica que la URL actual corresponda a la página de Login.
    4. Utiliza la función de navegación para volver a la página anterior.
    5. **Validación (Regreso):** Verifica que la URL actual sea la URL base (Home).

    Parámetros:
        set_up_Home (BasePage): Fixture que inicializa el navegador y navega a la URL base.

    Retorna:
        None: La prueba pasa si las validaciones de URL confirman la navegación correcta.
    """
    
    # El fixture `set_up_Home` ya ha realizado la navegación y el manejo de obstáculos.
    # Se asigna la instancia de BasePage a una variable local para mayor claridad.
    base_page = set_up_Home
    
    base_page.scroll_hasta_elemento(base_page.home.linkTestLogin, "scroll_HastaTestLogin", config.SCREENSHOT_DIR)    
    
    base_page.element.hacer_clic_en_elemento(base_page.home.linkTestLogin, "clic_ingresarALogin", config.SCREENSHOT_DIR)
    
    base_page.navigation.validar_url_actual(config.LOGIN_URL)
    
    base_page.navigation.volver_a_pagina_anterior("regrserAHome", config.SCREENSHOT_DIR)
    
    base_page.navigation.validar_url_actual(config.BASE_URL)
    
def test_ingresar_register_y_regresar_a_home(set_up_Home: BasePage) -> None:
    """
    [ID: HM-T004] Prueba la navegación de ida y vuelta entre la página de inicio
    y la sección 'Test Register'.

    Este test verifica que el usuario pueda acceder correctamente a la página de
    registro desde el home y que el uso de la funcionalidad 'volver' del navegador
    retorne exitosamente a la página principal (Home).

    Flujo:
    1. Scroll hasta el enlace 'Test Register' en la página principal.
    2. Hace clic en el enlace 'Test Register'.
    3. **Validación (Ida):** Verifica que la URL actual corresponda a la página de Registro.
    4. Utiliza la función de navegación para volver a la página anterior.
    5. **Validación (Regreso):** Verifica que la URL actual sea la URL base (Home).

    Parámetros:
        set_up_Home (BasePage): Fixture que inicializa el navegador y navega a la URL base.

    Retorna:
        None: La prueba pasa si las validaciones de URL confirman la navegación correcta.
    """
    
    # El fixture `set_up_Home` ya ha realizado la navegación y el manejo de obstáculos.
    # Se asigna la instancia de BasePage a una variable local para mayor claridad.
    base_page = set_up_Home
    
    base_page.scroll_hasta_elemento(base_page.home.linkTestRegister, "scroll_HastaTestRegister", config.SCREENSHOT_DIR)    
    
    base_page.element.hacer_clic_en_elemento(base_page.home.linkTestRegister, "clic_ingresarARegister", config.SCREENSHOT_DIR)
    
    base_page.navigation.validar_url_actual(config.REGISTER_URL)
    
    base_page.navigation.volver_a_pagina_anterior("regrserAHome", config.SCREENSHOT_DIR)
    
    base_page.navigation.validar_url_actual(config.BASE_URL)
    
def test_ingresar_dynamic_table_y_regresar_a_home(set_up_Home: BasePage) -> None:
    """
    [ID: HM-T005] Prueba la navegación de ida y vuelta entre la página de inicio
    y la sección 'Dynamic Table'.

    Este test verifica que el usuario pueda acceder correctamente a la página de
    tablas dinámicas desde el home y que el uso de la funcionalidad 'volver' del navegador
    retorne exitosamente a la página principal (Home).

    Flujo:
    1. Scroll hasta el enlace 'Dynamic Table' en la página principal.
    2. Hace clic en el enlace 'Dynamic Table'.
    3. **Validación (Ida):** Verifica que la URL actual corresponda a la página de Dynamic Table.
    4. Utiliza la función de navegación para volver a la página anterior.
    5. **Validación (Regreso):** Verifica que la URL actual sea la URL base (Home).

    Parámetros:
        set_up_Home (BasePage): Fixture que inicializa el navegador y navega a la URL base.

    Retorna:
        None: La prueba pasa si las validaciones de URL confirman la navegación correcta.
    """
    
    # El fixture `set_up_Home` ya ha realizado la navegación y el manejo de obstáculos.
    # Se asigna la instancia de BasePage a una variable local para mayor claridad.
    base_page = set_up_Home
    
    base_page.scroll_hasta_elemento(base_page.home.linkDynamicTable, "scroll_HastaTestDynamicTable", config.SCREENSHOT_DIR)    
    
    base_page.element.hacer_clic_en_elemento(base_page.home.linkDynamicTable, "clic_ingresarADinamicTable", config.SCREENSHOT_DIR)
    
    base_page.navigation.validar_url_actual(config.DYNAMICTABLE_URL)
    
    base_page.navigation.volver_a_pagina_anterior("regrserAHome", config.SCREENSHOT_DIR)
    
    base_page.navigation.validar_url_actual(config.BASE_URL)