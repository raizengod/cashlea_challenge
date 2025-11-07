import requests
from requests.auth import HTTPBasicAuth
from requests.utils import quote
import json
import os
from datetime import datetime
from utils.config import get_setting, FRAMEWORK_LOGGER 

jira_logger = FRAMEWORK_LOGGER

class JiraClient:
    """Clase para interactuar con la API de Jira (Crear/Actualizar Issues y adjuntar evidencias por URL)."""
    
    TRANSITIONS = {
            # Transición a 'Abierto/To Do'
            "TO DO": "11",
            # Transición a 'In Progress'
            "EN PROGRESO": "21",
            # Transición a 'ANALYZING'
            "ANALYZING": "2",
            # Transición a 'QA REVIEW'
            "QA REVIEW": "3",
            # Transición a 'Done/Closed'
            "DONE": "31",
    }
    
    def __init__(self):
        # Carga las credenciales y configuraciones desde utils/config
        self.base_url = get_setting('JIRA_URL').rstrip('/') # URL de tu instancia de Jira
        self.api_user = get_setting('JIRA_API_USER')       # Usuario de la API (generalmente un correo)
        self.api_token = get_setting('JIRA_API_TOKEN')     # Token de la API
        self.project_key = get_setting('JIRA_PROJECT_KEY') # Clave del proyecto (ej: "AT")
        self.issue_type = get_setting('JIRA_ISSUE_TYPE')   # Tipo de Issue (ej: "Bug")
        self.security_level_id = get_setting('JIRA_SECURITY_LEVEL_ID') # Opcional: Nivel de seguridad (ID numérico)

        # Autenticación HTTP Básica para Jira (Usuario y Token)
        self.auth = HTTPBasicAuth(self.api_user, self.api_token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        self.headers_attachment = {
            "X-Atlassian-Token": "no-check" # Necesario para adjuntar archivos
        }

        # USANDO LOGGER: Log de inicialización
        if all([self.base_url, self.api_user, self.api_token, self.project_key, self.issue_type]):
            jira_logger.info(f"\n✅ JiraClient: Inicializado con éxito. Proyecto: {self.project_key}, Tipo: {self.issue_type}.")
        else:
            jira_logger.warning(f"\n⚠️ JiraClient: Inicializado, pero faltan credenciales o configuraciones críticas. El reporte a Jira no funcionará correctamente.")

    # ----------------------------------------------------------------------
    # 1. BÚSQUEDA / DEDUPLICACIÓN
    # ----------------------------------------------------------------------
    def find_issue_by_test_id(self, test_case_id: str, environment: str, device: str) -> dict:
        """
        Busca un issue de Jira existente por su ID de caso de prueba, ambiente y dispositivo.
        
        Solo busca Issues que no estén en la categoría 'Done' (abiertos), lo que constituye 
        la lógica de deduplicación principal para evitar la creación de duplicados.
        """
        jira_logger.info(f"[JIRA-HANDLER] Buscando Issue existente (ID: {test_case_id}, Ambiente: {environment}, Dispositivo: {device})")
            
        # 1. Definir los tokens de búsqueda, escapando los caracteres especiales de Lucene
        #    para que el operador '~' busque la frase literal.
        
        # El token de Ambiente (ej: "qa") no requiere escape.
        token_environment = f"\"{environment}\"" 
    
        # Escapar paréntesis para JQL Lucene. Para obtener \\( en el JQL (escape correcto), se necesita \\\\( en Python.
        test_id_literal = f"({test_case_id})"
        # Usar 4 barras invertidas para generar la secuencia de escape de Lucene correcta (\\).
        test_id_escaped = test_id_literal.replace("(", "\\\\(").replace(")", "\\\\)") 
        token_test_id = f"\"{test_id_escaped}\"" 
        
        # Escapar corchetes para JQL Lucene. Para obtener \\[ en el JQL (escape correcto), se necesita \\\[ en Python.
        device_literal = f"[{device}]"
        # Usar 4 barras invertidas para generar la secuencia de escape de Lucene correcta (\\).
        device_escaped = device_literal.replace("[", "\\\\[").replace("]", "\\\\]") 
        token_device = f"\"{device_escaped}\"" 

        # 2. Construir el JQL combinando las 3 condiciones de búsqueda de texto (~), unidas por AND.
        jql_query = (
            f"project = {self.project_key} AND "
            f"summary ~ {token_environment} AND " 
            f"summary ~ {token_test_id} AND " 
            f"summary ~ {token_device} AND " 
            f"issuetype = \"{self.issue_type}\" AND "
            f"statusCategory != \"Done\""
        )
        
        url = f"{self.base_url}/rest/api/3/search/jql?jql={jql_query}&fields=summary,status&maxResults=1"
        jira_logger.debug(f"\nJQL generado: {jql_query}")

        try:
            response = requests.get(url, headers=self.headers, auth=self.auth)
            
            # ⚠️ Captura cualquier error HTTP (4xx, 5xx) usando raise_for_status()
            response.raise_for_status() 
            data = response.json()
            issues = data.get('issues', [])
        
            if issues:
                issue = issues[0]
                issue_summary = issue['fields']['summary']
                
                # 💡 MEJORA: Incluye el resumen completo y la etiqueta RE-FALLO
                jira_logger.info(
                    f"\n✅ Issue existente encontrado (RE-FALLO): {issue['key']} - '{issue_summary}' "
                    f"(Status: {issue['fields']['status']['name']})"
                )
                return {'key': issue['key'], 'status': issue['fields']['status']['name']}
            
            jira_logger.info("\n❌ No se encontró Issue existente para el test fallido.")
            return {}

        except requests.exceptions.RequestException as e:
            # 🔴 Manejar errores de conexión o HTTP (Timeouts, 500, 400 Bad Request)
            # Intenta obtener el cuerpo de la respuesta para obtener detalles de la API de Jira.
            error_details = getattr(e.response, 'text', 'No se pudo obtener la respuesta HTTP.')
            
            # Log más informativo para 400
            if 'response' in locals() and response.status_code == 400:
                # Error específico por JQL Inválido o mala petición al API
                jira_logger.critical(f"\n❌ ERROR CRÍTICO: Búsqueda de Issue fallida. JQL Inválido o Error en API (400 Bad Request). Detalles: {error_details}", exc_info=False)
            else:
                # Otros errores de conexión o HTTP (Auth, 500, etc.)
                jira_logger.critical(f"\n❌ ERROR CRÍTICO al comunicarse con Jira API (RequestException): {e}. Detalles: {error_details}", exc_info=False)
            return {}
        except Exception as e:
            # Captura errores de parseo o KeyError inesperado
            jira_logger.critical(f"\n❌ Error inesperado al procesar la respuesta de Jira: {e}", exc_info=False)
            return {}

    # ----------------------------------------------------------------------
    # 2. CREACIÓN DE ISSUE
    # ----------------------------------------------------------------------
    def create_issue(self, summary: str, description: str, labels: list[str] = None) -> tuple[str | None, str | None]:
        """Crea un nuevo Issue (Bug) en el proyecto configurado."""
        if not all([self.base_url, self.api_user, self.api_token, self.project_key, self.issue_type]):
            jira_logger.error(f"\n❌ Faltan credenciales o configuraciones críticas. Issue de falla NO creado.")
            return None, None # Retorna tupla (ID, KEY)

        # Lógica de security_field sin cambios
        security_field = {}
        if self.security_level_id and self.security_level_id not in ('N/A', ''): 
            security_field = {
                "security": {
                    "id": self.security_level_id
                }
            }
        
        # Añadir campo 'labels' si se proporciona.
        labels_field = {"labels": labels} if labels else {}

        payload = {
            "fields": {
                "project": {
                    "key": self.project_key
                },
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": description
                                }
                            ]
                        }
                    ]
                },
                "issuetype": {
                    "name": self.issue_type
                },
                **labels_field,
                **security_field 
            }
        }
        
        url = f"{self.base_url}/rest/api/3/issue"

        try:
            response = requests.post(url, headers=self.headers, json=payload, auth=self.auth)
            response.raise_for_status()
            response_json = response.json()
            issue_key = response_json.get('key')
            issue_id = response_json.get('id')
            jira_logger.info(f"\n✅ Issue Jira creado: '{issue_key}' (ID: {issue_id}, Proyecto: {self.project_key}).")
            return issue_key # Retorna tupla con ID y KEY
        except requests.exceptions.RequestException as e:
            error_details = response.text if 'response' in locals() else 'No se pudo obtener la respuesta HTTP.'
            jira_logger.error(f"\n❌ Error al crear el Issue Jira: {e}. Detalles del API: {error_details}", exc_info=True)
            return None, None

    # ----------------------------------------------------------------------
    # 3. COMENTAR ISSUE (RE-FALLO)
    # ----------------------------------------------------------------------
    def add_comment_to_issue(self, issue_key_or_id: str, comment: str) -> bool:
        """Añade un comentario a un Issue Jira existente."""
        if not all([self.base_url, self.api_user, self.api_token]):
            jira_logger.error(f"\n❌ Faltan credenciales. Comentario en Issue NO añadido.")
            return False
            
        url = f"{self.base_url}/rest/api/3/issue/{issue_key_or_id}/comment"
        
        payload = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": comment
                            }
                        ]
                    }
                ]
            }
        }

        try:
            response = requests.post(url, headers=self.headers, json=payload, auth=self.auth)
            response.raise_for_status()
            jira_logger.info(f"\n✅ Comentario añadido al Issue Jira: {issue_key_or_id}.")
            return True
        except requests.exceptions.RequestException as e:
            error_details = response.text if 'response' in locals() else 'No se pudo obtener la respuesta HTTP.'
            jira_logger.error(f"\n❌ Error al añadir comentario al Issue '{issue_key_or_id}': {e}. Detalles del API: {error_details}", exc_info=False)
            return False

    # ----------------------------------------------------------------------
    # 4. TRANSICIÓN DE ISSUE (MOVER A ESTADO)
    # ----------------------------------------------------------------------
    def transition_issue(self, issue_key_or_id: str, transition_name: str) -> bool:
        """
        Mueve un Issue a un estado específico (ej: 'Reopen', 'Done', 'Cerrado').
        Primero busca el ID de la transición por su nombre.
        """
        if not all([self.base_url, self.api_user, self.api_token]):
            jira_logger.error(f"\n❌ Faltan credenciales. Transición en Issue NO realizada.")
            return False

        # --- Sub-Paso 1: Obtener ID de la Transición ---
        url_transitions = f"{self.base_url}/rest/api/3/issue/{issue_key_or_id}/transitions"
        try:
            response = requests.get(url_transitions, headers=self.headers, auth=self.auth)
            response.raise_for_status()
            transitions = response.json().get('transitions', [])
            
            # Buscar el ID por el nombre de la transición (ej: "Done")
            transition_id = next(
                (t['id'] for t in transitions if t['name'].lower() == transition_name.lower()),
                None
            )

            if not transition_id:
                available_transitions = ", ".join([t['name'] for t in transitions])
                jira_logger.warning(f"\n⚠️ Transición '{transition_name}' no encontrada para el Issue {issue_key_or_id}. Transiciones disponibles: {available_transitions}")
                return False

        except requests.exceptions.RequestException as e:
            jira_logger.error(f"\n❌ Error al buscar transiciones para Issue {issue_key_or_id}: {e}", exc_info=False)
            return False

        # --- Sub-Paso 2: Ejecutar la Transición ---
        url_transition = f"{self.base_url}/rest/api/3/issue/{issue_key_or_id}/transitions"
        payload = {
            "transition": {
                "id": transition_id
            }
        }
        
        try:
            # Una transición exitosa devuelve un 204 No Content
            response = requests.post(url_transition, headers=self.headers, json=payload, auth=self.auth)
            response.raise_for_status()
            jira_logger.info(f"\n✅ Issue Jira {issue_key_or_id} transicionado exitosamente a: '{transition_name}'.")
            return True
        except requests.exceptions.RequestException as e:
            error_details = response.text if 'response' in locals() else 'No se pudo obtener la respuesta HTTP.'
            jira_logger.error(f"\n❌ Error al ejecutar transición a '{transition_name}' en Issue '{issue_key_or_id}': {e}. Detalles del API: {error_details}", exc_info=False)
            return False

    # ----------------------------------------------------------------------
    # 5. ADJUNTAR ARCHIVOS
    # ----------------------------------------------------------------------
    def attach_file_to_issue(self, issue_key_or_id: str, file_path: str) -> bool:
        """Adjunta un archivo local (screenshot, video, trace) al Issue Jira."""
        if not all([self.base_url, self.api_user, self.api_token]):
            jira_logger.error(f"\n❌ Faltan credenciales. Archivo NO adjuntado.")
            return False
        
        if not os.path.exists(file_path):
            jira_logger.warning(f"\n⚠️ Advertencia: Archivo a adjuntar no encontrado en la ruta: {file_path}")
            return False

        url = f"{self.base_url}/rest/api/3/issue/{issue_key_or_id}/attachments"

        try:
            with open(file_path, 'rb') as f:
                # El archivo debe enviarse como multipart/form-data.
                files = {'file': (os.path.basename(file_path), f)}
                
                # Se deben usar las cabeceras específicas de adjuntos
                response = requests.post(
                    url, 
                    headers=self.headers_attachment, 
                    files=files, 
                    auth=self.auth
                )
            
            response.raise_for_status()
            jira_logger.info(f"\n📎Archivo adjuntado a Jira: {os.path.basename(file_path)} al Issue {issue_key_or_id}.")
            return True

        except requests.exceptions.RequestException as e:
            error_details = response.text if 'response' in locals() else 'No se pudo obtener la respuesta HTTP.'
            jira_logger.error(f"\n❌ Error al adjuntar archivo '{os.path.basename(file_path)}' al Issue '{issue_key_or_id}': {e}. Detalles del API: {error_details}", exc_info=False)
            return False
            
    # Función de adjuntar URL no es necesaria en Jira (se añade en el comentario), 
    # pero se mantiene el método vacío por si se requiere en el futuro.
    def add_url_attachment(self, issue_key_or_id: str, url: str, display_name: str = "Link de Evidencia"):
         """En Jira, las URLs se adjuntan como un comentario, no como un 'attachment' directo del API."""
         comment = f"**{display_name}:** [Link de Evidencia]({url})"
         self.add_comment_to_issue(issue_key_or_id, comment)

# Nota: Para una implementación más robusta, se recomienda usar la librería oficial 'jira' de Python, 
# pero esta clase usa 'requests' para mantener la consistencia con el estilo del TrelloClient.