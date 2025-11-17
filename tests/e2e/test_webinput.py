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

@allure.id("WI-T001")
@allure.title("[ID: WI-T001] Verifica la presencia y el estado inicial de los elementos críticos en la página 'Web Input Examples'.")
def test_verificar_elementos_requeridos_presentes_web_inputs(set_up_WebInputs: BasePage) -> None:
    """
    [ID: WI-T001] Verifica la presencia y el estado inicial de los elementos
    críticos en la página 'Web Input Examples'.

    Este test asegura que el título, la descripción y los campos de entrada
    principales sean visibles, mientras que sus respectivos campos de salida (output)
    permanezcan ocultos por defecto, validando el estado inicial de la UI.

    Flujo de Verificación:
    1.  Desplazamiento (Scroll) hasta el área del título de la página.
    2.  **Validación de Contenido (Texto Exacto):** Verifica el título principal.
    3.  **Validación de Contenido (Texto Exacto):** Verifica el texto de la descripción.
    4.  **Validación de Visibilidad (Entradas):** Verifica que los 4 campos de entrada (numérico, alfabético, password, fecha) estén visibles.
    5.  **Validación de No Visibilidad (Salidas):** Verifica que los 4 campos de salida (output) permanezcan ocultos.

    Parámetros:
        set_up_WebInputs (BasePage): Fixture que navega previamente a la URL de
            'Web Input Examples' y proporciona la instancia
            de la Page Object Model.

    Retorna:
        None: La prueba pasa si todos los textos coinciden exactamente y los estados
            de visibilidad (visible/no visible) son los esperados.

    """
    # El fixture `set_up_WebInputs` ya ha realizado la navegación y el manejo de obstáculos.
    # Se asigna la instancia de BasePage a una variable local para mayor claridad.
    base_page = set_up_WebInputs
    
    base_page.scroll_hasta_elemento(base_page.webinputs.labelTituloWebInput, "scroll_HastaLabelWebInput", config.SCREENSHOT_DIR)
    
    base_page.element.verificar_texto_exacto(base_page.webinputs.labelTituloWebInput, 
                                             "Web inputs page for Automation Testing Practice",
                                             "verificar_textoExactoLabelTitulo", config.SCREENSHOT_DIR)
    
    texto_descripcion_esperado = (
        """Web inputs refer to the data or information provided by users through various input mechanisms on a website.
        Web inputs allow users to interact with web pages, submit forms, and provide data for processing.""")
    base_page.element.verificar_texto_exacto(base_page.webinputs.labelDescriptionWebInput, texto_descripcion_esperado,
                                             "verificarTextoDescripciónWebInputs", base_page.SCREENSHOT_BASE_DIR
                                             )
    
    base_page.element.validar_elemento_visible(base_page.webinputs.inputNumerico, "verificarCampoNuméricoVisible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.webinputs.inputAlfabetico, "verificarCampoAlfabéticoVisible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.webinputs.inputPassword, "verificarCampoPasswordVisible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.webinputs.inputFecha, "verificarCampoFechaVisible", config.SCREENSHOT_DIR)
    
    base_page.element.validar_elemento_no_visible(base_page.webinputs.outputNumerico, "verificarCampoNuméricoNoVisible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_no_visible(base_page.webinputs.outputAlfabetico, "verificarCampoAlfabéticoNoVisible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_no_visible(base_page.webinputs.outputPassword, "verificarCampoPasswordNoVisible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_no_visible(base_page.webinputs.outputFecha, "verificarCampoFechaNoVisible", config.SCREENSHOT_DIR)
    
@allure.id("WI-T002")
@allure.title("[ID: WI-T002] Prueba la funcionalidad 'Display Inputs' con todos los campos de entrada vacíos.")
def test_display_inputs_vacios(set_up_WebInputs: BasePage) -> None:
    """
    [ID: WI-T002] Prueba la funcionalidad "Display Inputs" con todos los campos
    de entrada vacíos.

    Este test verifica que, incluso cuando los campos de entrada (numérico, alfabético,
    contraseña, fecha) están vacíos, el sistema captura y muestra ese estado vacío
    en los campos de salida correspondientes al hacer clic en el botón de acción.

    Flujo:

    1.  Desplazamiento (Scroll) hasta los campos de entrada.
    2.  **Validación de Pre-condición:** Verifica que los 4 campos de entrada estén vacíos.
    3.  Hace clic en el botón 'Display Inputs'.
    4.  **Validación de Resultado:** Verifica que los 4 campos de salida (output)
        también se encuentren vacíos después de la acción.

    Parámetros:
        set_up_WebInputs (BasePage): Fixture que navega a la página 'Web Input Examples'
            y proporciona la instancia de la Page Object Model.

    Retorna:
        None: La prueba pasa si todos los campos de entrada y salida confirman estar vacíos.

    """
    # El fixture `set_up_WebInputs` ya ha realizado la navegación y el manejo de obstáculos.
    # Se asigna la instancia de BasePage a una variable local para mayor claridad.
    base_page = set_up_WebInputs
    
    # Nota: Se utiliza base_page.SCREENSHOT_BASE_DIR para la ruta dinámica
    base_page.scroll_hasta_elemento(base_page.webinputs.inputNumerico, "scroll_HastaCampoNumérico", config.SCREENSHOT_DIR)
    
    base_page.element.validar_elemento_vacio(base_page.webinputs.inputNumerico, "inputNuméricoVacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.webinputs.inputAlfabetico, "inputAlfabéticoVacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.webinputs.inputPassword, "inputPasswordVacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.webinputs.inputFecha, "inputFechaVacío", config.SCREENSHOT_DIR)
    
    base_page.element.hacer_clic_en_elemento(base_page.webinputs.btnDisplayInputs, "clic_botónDisplayInputs", config.SCREENSHOT_DIR)
    
    base_page.element.validar_elemento_vacio(base_page.webinputs.outputNumerico, "outputNuméricoVacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.webinputs.outputAlfabetico, "outputAlfabéticoVacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.webinputs.outputPassword, "outputPasswordVacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.webinputs.outputFecha, "outputFechaVacío", config.SCREENSHOT_DIR)
    
@allure.id("WI-T003")
@allure.title("[ID: WI-T003] Prueba el flujo completo de transferencia de datos, validando que los campos de salida (output) reflejen exactamente los datos ingresados en los campos de entrada.")
def test_output_con_data(set_up_WebInputs: BasePage) -> None:
    """
    [ID: WI-T003] Prueba el flujo completo de transferencia de datos, validando
    que los campos de salida (output) reflejen exactamente los datos ingresados
    en los campos de entrada.

    Este test simula la interacción del usuario llenando todos los campos de entrada
    con datos válidos generados por Faker y verifica la correcta proyección de esos
    datos en los campos de salida después de la acción 'Display Inputs'.

    Flujo:
    
    1.  Genera datos de prueba aleatorios (numérico, alfabético, password, fecha).
    2.  Desplazamiento (Scroll) hasta los campos de entrada.
    3.  Rellena los 4 campos de entrada (input) con los datos generados.
    4.  Hace clic en el botón 'Display Inputs'.
    5.  Desplazamiento (Scroll) hasta los campos de salida.
    6.  **Validación de Resultado:** Verifica que el valor de cada campo de salida
        coincida exactamente con el valor del dato que se ingresó inicialmente.

    Parámetros:
        set_up_WebInputs (BasePage): Fixture que navega previamente a la URL de
            'Web Input Examples' y proporciona la instancia
            de la Page Object Model.

    Retorna:
        None: La prueba pasa si el valor de los campos de salida es idéntico a
            los datos de entrada.

    """
    # El fixture `set_up_WebInputs` ya ha realizado la navegación y el manejo de obstáculos.
    # Se asigna la instancia de BasePage a una variable local para mayor claridad.
    base_page = set_up_WebInputs
    
    numerico = generador_datos.generar_numero_aleatorio()
    alfabetico = generador_datos.generar_palabra_corta()
    password = generador_datos.generar_password_segura()
    fecha = generador_datos.generar_fecha_nacimiento()
    
    base_page.scroll_hasta_elemento(base_page.webinputs.inputNumerico, "scroll_HastaCampoNumérico", config.SCREENSHOT_DIR)
    
    base_page.element.rellenar_campo_numerico_positivo(base_page.webinputs.inputNumerico, numerico ,"ingresarDatoNumérico", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.webinputs.inputAlfabetico, alfabetico ,"ingresarDatoAlfabético", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.webinputs.inputPassword, password ,"ingresarDatoPassword", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.webinputs.inputFecha, fecha ,"ingresarDatoFecha", config.SCREENSHOT_DIR)
    
    base_page.element.hacer_clic_en_elemento(base_page.webinputs.btnDisplayInputs, "clic_botónDisplayInputs", config.SCREENSHOT_DIR)
    
    base_page.scroll_hasta_elemento(base_page.webinputs.outputNumerico, "scroll_HastaCampoNumérico", config.SCREENSHOT_DIR)
    
    base_page.element.verificar_texto_exacto(base_page.webinputs.outputNumerico, str(numerico), "verificarValorOutputNuméricoVacío", config.SCREENSHOT_DIR)
    base_page.element.verificar_texto_exacto(base_page.webinputs.outputAlfabetico, alfabetico, "verificarValorOutputAlfabéticoVacío", config.SCREENSHOT_DIR)
    base_page.element.verificar_texto_exacto(base_page.webinputs.outputPassword, password, "verificarValorOutputPasswordVacío", config.SCREENSHOT_DIR)
    base_page.element.verificar_texto_exacto(base_page.webinputs.outputFecha, fecha, "verificarValorOutputFechaVacío", config.SCREENSHOT_DIR)
    
@allure.id("WI-T004")
@allure.title("[ID: WI-T004] Prueba el ciclo completo de ingreso, visualización y limpieza de datos utilizando los botones 'Display Inputs' y 'Clear Inputs'.")
def test_validar_clear_display_botón(set_up_WebInputs: BasePage) -> None:
    """
    [ID: WI-T004] Prueba el ciclo completo de ingreso, visualización y limpieza
    de datos utilizando los botones 'Display Inputs' y 'Clear Inputs'.

    Este test verifica que el flujo de datos funcione correctamente (input -> output)
    y, posteriormente, valida que el botón 'Clear Inputs' restablezca el estado
    tanto de los campos de entrada (vacíos) como de los campos de salida (no visibles).

    Flujo:
    
    1.  Genera datos de prueba aleatorios (numérico, alfabético, password, fecha).
    2.  Rellena los 4 campos de entrada (input).
    3.  Hace clic en 'Display Inputs'.
    4.  **Validación de Salida (Display):** Verifica que los 4 campos de salida (output)
        muestren el valor ingresado.
    5.  Hace clic en el botón 'Clear Inputs'.
    6.  **Validación de Limpieza (Input):** Verifica que los 4 campos de entrada estén vacíos.
    7.  **Validación de Estado (Output):** Verifica que los 4 campos de salida regresen
        al estado inicial, siendo no visibles.

    Parámetros:
        set_up_WebInputs (BasePage): Fixture que navega previamente a la URL de
            'Web Input Examples' y proporciona la instancia
            de la Page Object Model.

    Retorna:
        None: La prueba pasa si todos los pasos de validación (display y limpieza) son exitosos.

    """
    # El fixture `set_up_WebInputs` ya ha realizado la navegación y el manejo de obstáculos.
    # Se asigna la instancia de BasePage a una variable local para mayor claridad.
    base_page = set_up_WebInputs
    
    numerico = generador_datos.generar_numero_aleatorio()
    alfabetico = generador_datos.generar_palabra_corta()
    password = generador_datos.generar_password_segura()
    fecha = generador_datos.generar_fecha_nacimiento()
    
    base_page.scroll_hasta_elemento(base_page.webinputs.inputNumerico, "scroll_HastaCampoNumérico", config.SCREENSHOT_DIR)
    
    base_page.element.rellenar_campo_numerico_positivo(base_page.webinputs.inputNumerico, numerico ,"ingresarDatoNumérico", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.webinputs.inputAlfabetico, alfabetico ,"ingresarDatoAlfabético", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.webinputs.inputPassword, password ,"ingresarDatoPassword", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.webinputs.inputFecha, fecha ,"ingresarDatoFecha", config.SCREENSHOT_DIR)
    
    base_page.element.hacer_clic_en_elemento(base_page.webinputs.btnDisplayInputs, "clic_botónDisplayInputs", config.SCREENSHOT_DIR)
    
    base_page.element.verificar_texto_exacto(base_page.webinputs.outputNumerico, str(numerico), "verificarValorOutputNuméricoVacío", config.SCREENSHOT_DIR)
    base_page.element.verificar_texto_exacto(base_page.webinputs.outputAlfabetico, alfabetico, "verificarValorOutputAlfabéticoVacío", config.SCREENSHOT_DIR)
    base_page.element.verificar_texto_exacto(base_page.webinputs.outputPassword, password, "verificarValorOutputPasswordVacío", config.SCREENSHOT_DIR)
    base_page.element.verificar_texto_exacto(base_page.webinputs.outputFecha, fecha, "verificarValorOutputFechaVacío", config.SCREENSHOT_DIR)
    
    base_page.element.hacer_clic_en_elemento(base_page.webinputs.btnClearInputs, "clic_botónClearInputs", config.SCREENSHOT_DIR)
    
    base_page.scroll_hasta_elemento(base_page.webinputs.inputNumerico, "scroll_HastaCampoNumérico", config.SCREENSHOT_DIR)
    
    base_page.element.validar_elemento_vacio(base_page.webinputs.inputNumerico, "inputNuméricoVacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.webinputs.inputAlfabetico, "inputAlfabéticoVacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.webinputs.inputPassword, "inputPasswordVacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.webinputs.inputFecha, "inputFechaVacío", config.SCREENSHOT_DIR)
    
    base_page.element.validar_elemento_no_visible(base_page.webinputs.outputNumerico, "verificarCampoNuméricoNoVisible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_no_visible(base_page.webinputs.outputAlfabetico, "verificarCampoAlfabéticoNoVisible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_no_visible(base_page.webinputs.outputPassword, "verificarCampoPasswordNoVisible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_no_visible(base_page.webinputs.outputFecha, "verificarCampoFechaNoVisible", config.SCREENSHOT_DIR)