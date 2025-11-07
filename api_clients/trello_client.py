import requests
# Importar el logger y la función get_setting
from utils.config import get_setting, FRAMEWORK_LOGGER, TRELLO_REPORTING_ENABLED
# Necesario para obtener el nombre del archivo
import os

# Usamos el logger central del framework para todos los mensajes del cliente Trello
trello_logger = FRAMEWORK_LOGGER 

class TrelloClient:
    """Clase para interactuar con la API de Trello."""
    
    def __init__(self):
        # Carga las credenciales y los IDs de las listas usando utilidad de configuración
        self.api_key = get_setting('TRELLO_API_KEY') 
        self.api_token = get_setting('TRELLO_API_TOKEN') 
        
        # Carga de los TRES IDs de lista requeridos por el usuario
        self.fail_list_id = get_setting('TRELLO_FAIL_LIST_ID')
        self.qa_list_id = get_setting('TRELLO_QA_LIST_ID')
        self.ongoing_list_id = get_setting('TRELLO_ONGOING_LIST_ID')
        self.done_list_id = get_setting('TRELLO_DONE_LIST_ID')
        
        self.base_url_cards = "https://api.trello.com/1/cards"
        self.auth = {
            'key': self.api_key,
            'token': self.api_token
        }
        self.base_url_lists = "https://api.trello.com/1/lists"
        self.base_url_actions = "https://api.trello.com/1/actions"
        
        # USANDO LOGGER: Log de inicialización
        if all([self.api_key, self.api_token, self.fail_list_id, self.ongoing_list_id, self.done_list_id]):
            trello_logger.info(f"\n✅ TrelloClient: Inicializado con éxito. Listas (FAIL/ONGOING/DONE) cargadas.")
        else:
            trello_logger.warning(f"\n⚠️ TrelloClient: Inicializado, pero faltan credenciales o IDs de listas críticas. El reporte de Trello no funcionará correctamente.")

    def find_card_by_test_id(self, test_case_id: str, ambiente: str, navegador_dispositivo: str) -> str | None:
        """
        Busca una tarjeta en las listas de fallas, QA y On Going cuyo nombre contenga la combinación
        del ID del caso de prueba, el ambiente y el navegador/dispositivo.

        Args:
            test_case_id (str): El ID del caso de prueba (ej: 'HM-T001').
            ambiente (str): El ambiente de ejecución (ej: 'QA').
            navegador_dispositivo (str): El navegador y dispositivo de ejecución (ej: 'chromium-1920x1080').

        Retorna:
            str | None: El ID de la tarjeta si es encontrada, o None si no.
        """
        # Validación de credenciales y IDs de listas críticas para la búsqueda
        if not all([self.api_key, self.api_token, self.fail_list_id, self.qa_list_id, self.ongoing_list_id]):
            trello_logger.error("\n❌ Faltan credenciales o IDs de listas críticas. Búsqueda de tarjeta NO realizada.")
            return None
        
        # Criterios de búsqueda: (ID del caso) y [Navegador/Dispositivo] y Ambiente (para coincidir con el título de la tarjeta)
        search_criteria_id = f"({test_case_id})"
        search_criteria_ambiente = ambiente.upper()
        # Se busca el ID de parametrización, ya que se añadirá al título de la tarjeta
        search_criteria_navegador = f"[{navegador_dispositivo}]" 

        # Lista de IDs de listas a buscar, mapeadas por su nombre para el logging
        list_ids_to_search = {
            'FAIL': self.fail_list_id,
            'QA': self.qa_list_id,
            'ONGOING': self.ongoing_list_id
        }

        # Iterar sobre las 3 listas de Trello
        for list_name, list_id in list_ids_to_search.items():
            if not list_id:
                 trello_logger.warning(f"\n⚠️ ID de lista Trello no configurado para: {list_name}. Se omite la búsqueda en esta lista.")
                 continue

            url = f"{self.base_url_lists}/{list_id}/cards"
            params = {
                'fields': 'name',
                **self.auth 
            }
            
            trello_logger.debug(f"\n🔎 Buscando en lista: {list_name} (ID: {list_id}) con criterios: ID={test_case_id}, Amb={ambiente}, Nav={navegador_dispositivo}")

            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                cards = response.json()
                
                for card in cards:
                    card_name = card.get('name', '')
                    
                    # Criterios estrictos de coincidencia dentro del nombre de la tarjeta
                    if (search_criteria_id in card_name and 
                        search_criteria_ambiente in card_name and
                        search_criteria_navegador in card_name):
                        
                        trello_logger.info(f"\n🔎 Tarjeta duplicada encontrada en {list_name} para el test '{test_case_id}' en '{navegador_dispositivo}' (ID de Trello: {card['id']}).")
                        # 🚨 Retornar un diccionario con los IDs y el nombre de la lista.
                        return {
                            'id': card['id'],
                            'idList': list_id, # Usamos el ID de la lista que estamos iterando
                            'list_name': list_name # Usamos el nombre de la lista que estamos iterando
                        }
                
            except requests.exceptions.RequestException as e:
                error_details = response.text if 'response' in locals() else 'No se pudo obtener la respuesta HTTP.'
                trello_logger.error(f"\n❌ Error al buscar tarjetas en la lista {list_name}: {e}. Detalles del API: {error_details}", exc_info=False)
                continue 

        trello_logger.debug(f"\n🔎 No se encontró tarjeta para los criterios: ID '{test_case_id}', Amb '{ambiente}', Nav '{navegador_dispositivo}'.")
        return None
    
    def create_card(self, name: str, description: str):
        """Crea una nueva tarjeta en la lista de fallas configurada."""
        if not all([self.api_key, self.api_token, self.fail_list_id]):
            trello_logger.error(f"\n❌ Faltan credenciales o el FAIL_LIST_ID. Tarjeta de falla NO creada.")
            return

        payload = {
            'idList': self.fail_list_id, # Usando el ID de la lista de fallas
            'name': name,
            'desc': description,
            **self.auth 
        }
        
        try:
            response = requests.post(self.base_url_cards, data=payload)
            response.raise_for_status()
            response_json = response.json()
            trello_logger.info(f"\n✅ Tarjeta Trello creada: '{name}' (ID corto: {response_json.get('idShort')}, Lista: FAIL)")
            return response_json
        except requests.exceptions.RequestException as e:
            error_details = response.text if 'response' in locals() else 'No se pudo obtener la respuesta HTTP.'
            trello_logger.error(f"\n❌ Error al crear la tarjeta Trello: {e}. Detalles del API: {error_details}", exc_info=True)
            return None
        
    def add_comment_to_card(self, card_id: str, comment: str) -> bool:
        """
        Añade un comentario a una tarjeta Trello existente.

        Args:
            card_id (str): El ID de la tarjeta donde se añadirá el comentario.
            comment (str): El texto del comentario a añadir.

        Retorna:
            bool: True si el comentario fue añadido exitosamente, False en caso contrario.
        """
        # 1. Validar que tenemos los IDs necesarios
        if not all([self.api_key, self.api_token, card_id]):
            trello_logger.error("\n❌ Faltan credenciales o el ID de la tarjeta para añadir el comentario.")
            return False

        # El endpoint para añadir un comentario a una tarjeta
        url = f"{self.base_url_cards}/{card_id}/actions/comments"
        
        # El payload debe incluir el texto del comentario y las credenciales de autenticación
        payload = {
            'text': comment,
            **self.auth 
        }
        
        try:
            # Trello usa un POST para añadir comentarios
            response = requests.post(url, data=payload)
            response.raise_for_status() # Lanza una excepción para códigos de estado 4xx/5xx

            # No es necesario el JSON de respuesta, solo verificar el estado
            trello_logger.info(f"\n💬 Comentario añadido exitosamente a la tarjeta Trello (ID: {card_id}).")
            return True
            
        except requests.exceptions.RequestException as e:
            error_details = response.text if 'response' in locals() else 'No se pudo obtener la respuesta HTTP.'
            trello_logger.error(f"\n❌ Error al añadir comentario a la tarjeta {card_id}: {e}. Detalles del API: {error_details}", exc_info=False)
            return False
        
    # Para adjuntar archivos
    def attach_file_to_card(self, card_id: str, file_path: str):
        """Adjunta un archivo local (screenshot, trace, video) a la tarjeta Trello especificada."""
        if not all([self.api_key, self.api_token, card_id, file_path]):
            trello_logger.error("\n❌ Faltan datos (ID de tarjeta, ruta del archivo o credenciales) para adjuntar archivo.")
            return False

        url = f"{self.base_url_cards}/{card_id}/attachments"
        
        try:
            # 1. Preparar el archivo para la carga
            with open(file_path, 'rb') as f:
                # 'file' es el nombre de campo esperado por la API de Trello
                files = {'file': (os.path.basename(file_path), f)}
                
                # 2. Enviar la solicitud POST
                # La autenticación se pasa en 'data'
                response = requests.post(url, data=self.auth, files=files)
                response.raise_for_status()
                
                trello_logger.info(f"\n📎 Archivo adjunto a la tarjeta {card_id} exitosamente: {os.path.basename(file_path)}")
                return True

        except FileNotFoundError:
            trello_logger.error(f"\n❌ Error al adjuntar archivo: Archivo no encontrado en la ruta: {file_path}")
            return False
        except requests.exceptions.RequestException as e:
            error_details = response.text if 'response' in locals() else 'No se pudo obtener la respuesta HTTP.'
            trello_logger.error(f"\n❌ Error al adjuntar archivo a la tarjeta Trello (ID: {card_id}): {e}. Detalles del API: {error_details}", exc_info=True)
            return False
        
    def attach_video_to_card(self, card_id: str, video_path: str):
        """Adjunta ÚNICAMENTE el archivo de video (evidencia de éxito) a la tarjeta Trello especificada."""
        # 1. Validaciones iniciales
        if not all([self.api_key, self.api_token, card_id, video_path]):
            trello_logger.error("\n❌ Faltan datos (ID de tarjeta, ruta del video o credenciales) para adjuntar video.")
            return False

        url = f"{self.base_url_cards}/{card_id}/attachments"
        
        try:
            # 2. Preparar el archivo de video para la carga
            # NOTA: Se asume que la ruta (video_path) es correcta y el archivo existe.
            with open(video_path, 'rb') as f:
                # 'file' es el nombre de campo esperado por la API de Trello
                files = {'file': (os.path.basename(video_path), f)}
                
                # 3. Enviar la solicitud POST
                # La autenticación se pasa en 'data'
                response = requests.post(url, data=self.auth, files=files)
                response.raise_for_status()
                
                trello_logger.info(f"\n🎥 **Evidencia de video adjunta a la tarjeta {card_id} exitosamente: {os.path.basename(video_path)}")
                return True

        except FileNotFoundError:
            trello_logger.error(f"\n❌ Error al adjuntar video: Archivo no encontrado en la ruta: {video_path}")
            return False
        except requests.exceptions.RequestException as e:
            error_details = response.text if 'response' in locals() else 'No se pudo obtener la respuesta HTTP.'
            trello_logger.error(f"\n❌ Error al adjuntar video a la tarjeta Trello (ID: {card_id}): {e}. Detalles del API: {error_details}", exc_info=True)
            return False
        
    def move_card(self, card_id: str, new_list_name: str):
        """Mueve una tarjeta existente a otra lista (Ongoing o Done)."""
        new_list_id = None
        
        # 1. Determinar el ID de la nueva lista a partir del nombre
        if new_list_name.upper() == 'FAIL':
            new_list_id = self.fail_list_id
        elif new_list_name.upper() == 'QA':
            new_list_id = self.qa_list_id
        elif new_list_name.upper() == 'ONGOING':
            new_list_id = self.ongoing_list_id
        elif new_list_name.upper() == 'DONE':
            new_list_id = self.done_list_id
        else:
            trello_logger.error(f"\n❌ Nombre de lista '{new_list_name}' no soportado para mover tarjeta. Use 'FAIL', 'QA', 'ONGOING' o 'DONE'.")
            return None

        # 2. Validar que tenemos los IDs necesarios
        if not all([self.api_key, self.api_token, card_id, new_list_id]):
            trello_logger.error("\n❌ Faltan credenciales o el ID de la tarjeta/lista destino para mover la tarjeta.")
            return

        url = f"{self.base_url_cards}/{card_id}"
        payload = {
            'idList': new_list_id,
            **self.auth
        }
        
        try:
            response = requests.put(url, data=payload)
            response.raise_for_status() 
            trello_logger.info(f"\n✅ Tarjeta Trello (ID: {card_id}) movida exitosamente a la lista: {new_list_name.upper()}.")
            return response.json()
        except requests.exceptions.RequestException as e:
            error_details = response.text if 'response' in locals() else 'No se pudo obtener la respuesta HTTP.'
            trello_logger.error(f"\n❌ Error al mover la tarjeta Trello (ID: {card_id}): {e}. Detalles del API: {error_details}", exc_info=True)
            return None