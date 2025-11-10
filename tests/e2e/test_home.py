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
    [ID: HM-T001]
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
    [ID: HM-T002]
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
    [ID: HM-T003]
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
    [ID: HM-T004]
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
    [ID: HM-T005]
    """
    
    # El fixture `set_up_Home` ya ha realizado la navegación y el manejo de obstáculos.
    # Se asigna la instancia de BasePage a una variable local para mayor claridad.
    base_page = set_up_Home
    
    base_page.scroll_hasta_elemento(base_page.home.linkDynamicTable, "scroll_HastaTestDynamicTable", config.SCREENSHOT_DIR)    
    
    base_page.element.hacer_clic_en_elemento(base_page.home.linkDynamicTable, "clic_ingresarADinamicTable", config.SCREENSHOT_DIR)
    
    base_page.navigation.validar_url_actual(config.DYNAMICTABLE_URL)
    
    base_page.navigation.volver_a_pagina_anterior("regrserAHome", config.SCREENSHOT_DIR)
    
    base_page.navigation.validar_url_actual(config.BASE_URL)