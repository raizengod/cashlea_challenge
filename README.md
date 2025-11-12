# 🧪 Prueba Técnica QA Automation: Cashela Challenge

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/raizengod/cashlea_challenge)

## 🐍 Playwright + Python + Pytest
Este proyecto contiene el framework de automatización de pruebas de extremo a extremo (E2E) desarrollado para cumplir con los requisitos de la Prueba Técnica de QA Automation para Cashela, enfocándose en la evaluación exploratoria y la implementación de un código robusto.

El Sistema Bajo Prueba (SUT) es el sitio de demostración pública: https://practice.expandtesting.com/

## 🎯 Objetivo de la automatización
El objetivo principal de la prueba fue evaluar la capacidad para analizar, estructurar y automatizar pruebas en un entorno con documentación incompleta, desde una perspectiva exploratoria.

Se buscó:

* Entender y validar los flujos principales del SUT (Login, Registro, Formularios).

* Implementar un framework utilizando Playwright y Python bajo el patrón Page Object Model (POM).

* Identificar y documentar defectos, incluyendo bugs funcionales, de seguridad y recomendaciones arquitectónicas.

## 🛠️ Tecnologías Utilizadas
**Core**
* **Python 3.13.9:** Lenguaje de programación.
* **Playwright:** Librería de automatización de navegadores.

**Testing**
* **Pytest:** Framework de pruebas.

**Datos**
* **Faker:** Módulo para la generación de datos de prueba.

**Reporte**
* **Allure:** Generación de reportes detallados y traza de fallos.
* **pytest-reporter-html1:**  Generación de informes HTML interactivo, proporcionando una visualización clara y detallada de los resultados.

**Diseño**
* **Page Object Model (POM):** Estructura del código para alta mantenibilidad y reusabilidad.

## 📂 Estructura del Proyecto
El proyecto está organizado siguiendo el patrón Page Object Model (POM), garantizando la separación de la lógica de prueba y los selectores de la interfaz de usuario.

* `tests/:` Contiene todos los archivos de prueba (`test_*.py`) con la lógica de las validaciones.

* `pages/:` Contiene los Page Objects, donde se definen los selectores y los métodos de interacción con la UI.

* `utils/:` Módulos utilitarios como el `config.py` y `generador_datos.py` (para persistencia de usuarios y generación de datos).

* `conftest.py:` Maneja las fixtures de Pytest, incluyendo la inicialización del navegador (Playwright).

## 📊 Flujos de Prueba Cubiertos

Se automatizaron un total de **13 casos de prueba** cubriendo 3 flujos críticos con enfoque en casos positivos, negativos y de control de errores.

```
ID    |        Flujo          |   Clave Cobertura         |   Notas de la Implementación
=========================================================================================================
F-01  |   Registro            |   100% (Casos Positivos   |   Se genera y persiste un usuario 
      |   (test_register.py)  |   y Negativos)            |   único y válido en un archivo JSON 
      |                       |                           |   para ser consumido en el flujo de Login.
---------------------------------------------------------------------------------------------------------
F-02  |   Autenticación       |   100% (Login Exitoso/    |   El test de Login Exitoso consume las 
      |   (test_login.py)     |   Fallido, Logout)        |   credenciales válidas persistidas por 
      |                       |                           |   el test de Registro, asegurando 
---------------------------------------------------------------------------------------------------------
F-03  |   Interacción         |   100% (Validación de     |   Verificación de que los campos de entrada 
      |   (test_webinput.py)  |   Tipos de Datos)         |   aceptan y reflejan correctamente los tipos 
      |                       |                           |   de datos (numérico, alfabético, password, 
      |                       |                           |   fecha).
```

## ⚙️ Configuración de Variables de Entorno (Requisito Crítico)

El framework utiliza **`python-dotenv`** para la gestión de variables de entorno, lo cual es esencial para separar credenciales y configuraciones por ambiente.

🚨 **CREACIÓN DEL ARCHIVO `environments/ambiente.env`**

Para la correcta ejecución del framework y, crucialmente, para la **Integración con Trello, Jira**, **DEBES** crear un archivo llamado **`[nombre_ambiente].env`** dentro del directorio **`environments/`** de la raíz del proyecto. Este archivo debe contener las siguientes variables de entorno:

```dotenv
BASE_URL=https://practice.expandtesting.com
LOGIN_URL=https://practice.expandtesting.com/login
REGISTER_URL=https://practice.expandtesting.com/register
WEBINPUT_URL=https://practice.expandtesting.com/inputs
DYNAMICTABLE_URL=https://practice.expandtesting.com/dynamic-table
USERDASHBOARD_URL=https://practice.expandtesting.com/secure

# Credenciales de la API de Trello (Necesarias para la sincronización)
TRELLO_API_KEY=
TRELLO_API_TOKEN=
# IDs de las listas en tu tablero de Trello
TRELLO_FAIL_LIST_ID= # ID de la lista donde se reportan los fallos
TRELLO_QA_LIST_ID= # ID de la lista para tarjetas movidas a QA para revisión manual
TRELLO_ONGOING_LIST_ID= # ID de la lista para casos en curso/ejecución
TRELLO_DONE_LIST_ID= # ID de la lista para casos de prueba cerrados/pasados
TRELLO_REPORTING_ENABLED= # Para activar o desactivar la creación de card en trello. Acepta valor True / False

# Credenciales de la API de Jira (Necesarias para la sincronización)
JIRA_REPORTING_ENABLED= # Para activar o desactivar la creación de card en Jira. Acepta valor True / False
JIRA_URL= # URL base de tu Jira (ej: `https://mi-empresa.atlassian.net`).
JIRA_API_USER=  # Correo electrónico de tu cuenta de Jira.
JIRA_API_TOKEN= # El token de API generado en Jira para autenticación.
JIRA_PROJECT_KEY= # La clave del proyecto donde se crearán los Issues (ej: `AE`).
JIRA_ISSUE_TYPE= # El tipo de Issue a crear (ej: `Bug` o `Error`).
JIRA_SECURITY_LEVEL_ID= #**Opcional**. ID numérico si tu proyecto requiere un nivel de seguridad.

# [Otras variables del ambiente, ej: BASE_URL, etc.]
```
## ⚙️ Configuración e Instalación
**Clonar el repositorio:**

```bash
git clone https://github.com/raizengod/cashlea_challenge.git
cd cashlea_challenge
```

**Crear y activar un entorno virtual (recomendado):**

```bash
python -m venv mv_CC
# En Windows
.\venv\Scripts\activate
# En macOS/Linux
source venv/bin/activate
```

**Instalar las dependencias:**

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
playwright install  # Instala los navegadores necesarios (Chromium, Firefox, WebKit)
# (Asegúrate de que pytest-reporter-html1 esté incluido en requirements.txt)
```

Asegurar Directorios de Evidencias: El archivo config.py define una función ensure_directories_exist() que crea automáticamente las carpetas necesarias para reportes y archivos de datos. Asegúrate de que esta función se ejecute, o créalas manualmente según la Estructura del Proyecto.

## 🚀 Uso
Para ejecutar el suite de pruebas para un entorno específico (por ejemplo, QA), utiliza la variable de entorno ENVIRONMENT o el argumento --env-file.

1.  **Usando la variable de entorno**
    (Recomendado para CI/CD y automatización)

    ```bash
    # En Windows
    set ENVIRONMENT=qa && pytest -n 4
    ```

    ```bash
    # En macOS/Linux
    ENVIRONMENT=qa pytest -n 4
    ```

2.  **Usando el argumento --env-file**
    (Útil para ejecuciones manuales y debugging)

    ```bash
    pytest -n 4 --env-file=environments/qa.env
    ```
3.  **Ejecuta prueba de módulo especifico**
    ```bash
    pytest tests\e2e\test_register.py
    ```

2.  **Ejecutar todas las pruebas con Pytest:**
    ```bash
    pytest tests
    ```

3.  **Ejecutar pruebas específicas (ejemplo):**
    ```bash
    pytest tests\e2e\test_login.py::test_hacer_logout_exitoso
    ```

4.  **Ejecuta las pruebas en paralelo y genera los resultados de reporte:**
    ```bash
    pytest test\e2e -n 8
    ```

5.  **Ejecutar las Pruebas:** El framework está configurado para generar resultados de `Allure` y `pytest-reporter-html1` automáticamente

## 📊 Instrucciones de Reporte
Una vez finalizada la ejecución de `pytest`, se han generado los resultados brutos necesarios para visualizar los informes de calidad.

1. **Visualizar Reporte de Allure**

El reporte de Allure ofrece una visión detallada, con pasos, logs, capturas y tiempos de ejecución.

* **Generar y Abrir el Reporte:**
    ```
    # Genera el reporte HTML a partir de los resultados brutos
    allure serve allure-results
    ```

2. **Visualizar Reporte Pytest-Reporter-HTML1**
Este reporte es un archivo HTML simple y autocontenido, fácil de abrir directamente.

* **Abrir el Archivo:** Busca y abre el archivo en tu navegador:
    ```
    open reports/html1/playwright_reporte.html

    # O ir a la carpeta reports/html1/ y abriir manualmente el archivo playwright_reporte.html
    ```


## 🚨 Hallazgos y Defectos Clave

Durante el testing exploratorio y la automatización, se detectaron 9 defectos, incluyendo dos bugs de seguridad críticos de alta prioridad:
```
Tipo de Defecto     |   Prioridad   |       Impacto
=============================================================================
Seguridad Crítica   |   ALTA        |   Enumeración de Usuarios: El sistema 
                    |               |   revela si el error en Login se debe a 
                    |               |   que el username no existe (mensaje 
                    |               |   "Your username is invalid!"), 
                    |               |   permitiendo la validación de miles 
                    |               |   de usuarios.
------------------------------------------------------------------------------
Seguridad Crítica   |   ALTA        |   Diferenciación de Error: El sistema 
                    |               |   distingue entre usuario y contraseña 
                    |               |   incorrectos (ej. "Your password is 
                    |               |   invalid!"), confirmando la existencia 
                    |               |   de un usuario válido a un atacante.
------------------------------------------------------------------------------
Arquitectónico      |   MEDIA       |   Reutilización de Selector: El selector 
                    |               |   #username se usa tanto para el <input> 
                    |               |   de Login como para el mensaje de 
                    |               |   bienvenida (<span>) en el Dashboard, 
                    |               |   comprometiendo la mantenibilidad y la 
                    |               |   robustez del POM.
```
**Ver Informe Consolidado de Defectos y Recomendaciones (Documento Completo)**

## 🌐 Estrategia de CI/CD

El framework está diseñado para una fácil integración en cualquier pipeline de Integración Continua (CI/CD) como GitHub Actions, Jenkins o GitLab CI.

* **Comando Simple:** El runner de CI solo necesita ejecutar: `pip install -r requirements.txt` y `pytest tests/`.

* **Datos Persistentes:** Se implementó una estrategia de persistencia de datos donde el test de Registro guarda las credenciales en un archivo. Esto asegura que el test de Login Exitoso siempre tendrá un usuario válido disponible, incluso en ejecuciones limpias de CI/CD.

## 🚀 Mejoras Futuras / Roadmap
* Explorar la automatización de otros módulos complejos como **Data Tables** y **Alerts**

## 🧠 Habilidades Demostradas

Este framework demuestra habilidades avanzadas en:

* **Diseño y Arquitectura de Frameworks:** Implementación robusta del patrón **Page Object Model (POM)** con capas de abstracción para elementos y validaciones, asegurando la mantenibilidad.
* **Gestión de Datos:** Implementación de la librería **Faker** para la generación dinámica de datos y una estrategia de persistencia (`registros_exitosos.json`) para asegurar la trazabilidad y la validez de los tests de Login, incluso en CI/CD.
* **Configuración y Ambientes:** Uso de archivos de configuración (`config.py`) y gestión de secretos para la ejecución multi-ambiente.
* **Logging y Trazabilidad:** Centralización de la lógica de logging y manejo de excepciones.
* **Reportes de Calidad:** Configuración de **Allure** y **pytest-reporter-html1** para generar informes detallados.
* **Integración Continua (CI/CD):** Diseño del workflow en GitHub Actions para la ejecución automatizada y el despliegue del reporte Allure en GitHub Pages.
* **UX Performance Testing:** Integración de la medición de métricas de rendimiento (tiempos de respuesta de UI) directamente en las pruebas funcionales.

## Autor
[Carlos N](https://github.com/raizengod)