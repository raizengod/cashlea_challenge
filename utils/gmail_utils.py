import base64
import os
import time
import logging

from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError, UnknownApiNameOrVersion

# Si el archivo está dentro de la carpeta 'utils', simplemente obtenemos un logger
# que será configurado por 'config.py' al inicio del framework.
logger = logging.getLogger('GmailUtils') 

# --- Excepciones Personalizadas para Diagnóstico ---
class GmailUtilsError(Exception):
    """Excepción base para errores específicos del módulo Gmail."""
    pass

class GmailAuthenticationError(GmailUtilsError):
    """Excepción lanzada si el servicio no se puede construir por falta de credenciales."""
    pass
# ----------------------------------------------------

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    """Retorna el objeto de servicio de la Gmail API, manejando la autenticación."""
    creds = None
    
    # --- 1. Cargar o Reportar Falta de Credenciales ---
    if os.path.exists('token.json'):
        logger.info("\nCargando credenciales desde 'token.json'.")
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        except Exception as e:
            logger.error(f"\nError al cargar 'token.json'. ¿Está corrupto? Detalles: {e}", exc_info=True)
            raise GmailAuthenticationError(f"\nToken de autenticación corrupto: {e}")
    else:
        logger.warning("\nArchivo 'token.json' no encontrado.")
        # Elevamos una excepción si el token no existe, ya que el servicio fallará sin él.
        raise GmailAuthenticationError("\nToken de autenticación (token.json) no encontrado. Ejecute setup_gmail_api.py.")

    # --- 2. Refrescar Token si es Necesario ---
    if creds and creds.expired and creds.refresh_token:
        logger.info("\nToken expirado. Refrescando el token de acceso...")
        try:
            creds.refresh(Request())
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
            logger.info("\nToken refrescado y guardado exitosamente.")
        except Exception as e:
            logger.critical(f"\nError FATAL al refrescar el token: {e}")
            raise GmailAuthenticationError(f"\nFallo al refrescar el token: {e}. Re-ejecute setup_gmail_api.py.")
    
    # --- 3. Construir y Retornar el Servicio ---
    try:
        service = build('gmail', 'v1', credentials=creds)
        logger.debug("\nServicio de Gmail API construido exitosamente.")
        return service
    except UnknownApiNameOrVersion as e:
        logger.error(f"\nError de construcción de la API: {e}. Verifique que la API esté habilitada en Google Cloud.", exc_info=True)
        raise GmailUtilsError(f"\nError de configuración de la API de Google: {e}")
    except Exception as e:
        logger.critical(f"\nFallo inesperado al construir el servicio: {e}", exc_info=True)
        raise GmailUtilsError(f"\nFallo al construir el servicio de Gmail: {e}")


def find_email(subject_line, sender_email, wait_timeout=30):
    """
    Busca un email por asunto y remitente en la bandeja de entrada, con reintentos.
    
    :param subject_line: El texto esperado en el asunto.
    :param sender_email: El email del remitente.
    :param wait_timeout: Tiempo máximo de espera en segundos.
    :return: El cuerpo HTML del email encontrado o None.
    """
    try:
        service = get_gmail_service()
    except GmailAuthenticationError as e:
        logger.critical(f"\nFALLO DE AUTENTICACIÓN. No se puede buscar el email: {e}")
        # Retorna None si el servicio no está disponible por problemas de autenticación.
        return None
        
    query = f"subject:\"{subject_line}\" from:{sender_email}"
    logger.info(f"\nIniciando búsqueda de email con QUERY: '{query}' por un máximo de {wait_timeout} segundos.")
    
    start_time = time.time()
    
    while time.time() - start_time < wait_timeout:
        try:
            # 1. Llama a la API para obtener una lista de IDs de mensajes
            response = service.users().messages().list(userId='me', q=query, maxResults=1).execute()
            messages = response.get('messages', [])
            
            if messages:
                email_id = messages[0]['id']
                logger.info(f"\nEmail encontrado! ID: {email_id}. Obteniendo contenido...")
                
                # 2. Obtiene el contenido del mensaje
                msg = service.users().messages().get(userId='me', id=email_id, format='full').execute()
                
                # 3. Procesa el cuerpo (busca la parte HTML)
                parts = msg.get('payload', {}).get('parts')
                if parts:
                    for part in parts:
                        # La estructura del email puede ser anidada, esta es una simplificación común
                        if part.get('mimeType') == 'text/html' and 'data' in part.get('body', {}):
                            data = part['body']['data']
                            # El cuerpo está codificado en Base64 URL Safe
                            decoded_body = base64.urlsafe_b64decode(data).decode('utf-8')
                            logger.info("\nCuerpo HTML decodificado exitosamente.")
                            return decoded_body
                    
                # Si el bucle termina sin retornar, significa que no se encontró el cuerpo HTML.
                logger.warning("\nEmail encontrado, pero no se pudo decodificar el cuerpo HTML o la estructura es inesperada.")
                return "Email encontrado, pero no se pudo decodificar el cuerpo HTML."
                
        except HttpError as e:
            # Captura errores específicos de la API de Google (ej. 403, 500)
            logger.error(f"\nError de la Gmail API (HTTP Error {e.resp.status}): {e}", exc_info=True)
            if e.resp.status == 403:
                logger.critical("\nError 403: Permisos denegados. ¡Verifique los SCOPES y que el usuario de prueba esté activo!")
                # Si es un error de permisos 403, no tiene sentido seguir reintentando.
                break 
            
        except Exception as e:
            # Captura otros errores inesperados (ej. problemas de red, fallo al decodificar base64)
            logger.error(f"\nError inesperado durante la búsqueda de email: {e}", exc_info=True)
            pass # Continúa el bucle de espera en caso de error temporal

        logger.info(f"\nEmail no encontrado. Reintentando en 5 segundos... ({int(time.time() - start_time)}/{wait_timeout}s)")
        time.sleep(5)
        
    logger.warning(f"\nBúsqueda de email fallida tras {wait_timeout} segundos.")
    return None