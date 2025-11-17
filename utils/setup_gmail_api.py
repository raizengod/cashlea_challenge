import os.path
import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError, UnknownApiNameOrVersion
from google.auth.exceptions import RefreshError # Para capturar fallos específicos de refresh

# --- Configuración de Logger y Excepción ---
# Asumimos que el framework (config.py) ya inicializó el logger.
logger = logging.getLogger('GmailSetup')

class GmailSetupError(Exception):
    """Excepción para errores críticos en el script de autenticación."""
    pass
# ---------------------------------------------

# Define los scopes de acceso que solicitaste
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service_creds():
    """
    Realiza el flujo de autenticación para obtener o refrescar las credenciales.
    Genera el archivo token.json después de la primera autenticación exitosa.
    """
    creds = None
    
    # 1. Intentar cargar un token existente
    if os.path.exists('token.json'):
        logger.info("\nArchivo 'token.json' encontrado. Cargando credenciales.")
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        except Exception as e:
            logger.error(f"\nError al cargar 'token.json': {e}. Se intentará un nuevo flujo de autenticación.", exc_info=True)

    # 2. Verificar y Autenticar si no es válido
    if not creds or not creds.valid:
        
        # 2a. Refrescar Token
        if creds and creds.expired and creds.refresh_token:
            logger.info("\nToken expirado pero tiene refresh_token. Intentando refrescar...")
            try:
                creds.refresh(Request())
                logger.info("\nToken refrescado exitosamente.")
            except RefreshError as e:
                logger.error(f"\nFALLO CRÍTICO al refrescar el token: {e}. Se requiere re-autenticación.", exc_info=True)
                creds = None # Forzar el flujo completo
            except Exception as e:
                logger.error(f"\nError inesperado durante el refresco del token: {e}. Se requiere re-autenticación.", exc_info=True)
                creds = None # Forzar el flujo completo
        
        # 2b. Flujo de Autenticación Completo (si no se pudo refrescar o no existe token)
        if not creds or not creds.valid:
            logger.info("\nIniciando flujo de autenticación completo (Browser Flow)...")
            
            # Verificar la existencia de credentials.json
            if not os.path.exists('credentials.json'):
                error_msg = "Archivo 'credentials.json' NO encontrado. ¡Necesitas descargarlo de Google Cloud!"
                logger.critical(error_msg)
                raise GmailSetupError(error_msg)
                
            try:
                # El archivo credentials.json es el que descargaste de Google Cloud
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES
                )
                # Esto abrirá una ventana en tu navegador para que inicies sesión y des permiso
                logger.info("\nPor favor, visita la URL en tu navegador para autorizar la aplicación.")
                creds = flow.run_local_server(port=0)
                logger.info("\nFlujo de autenticación completado por el usuario.")
                
            except Exception as e:
                logger.critical(f"\nFALLO CRÍTICO en el flujo de autenticación del navegador: {e}", exc_info=True)
                raise GmailSetupError(f"\nFallo en la autenticación de Google: {e}")

        # 3. Guardar las Credenciales
        if creds:
            try:
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
                logger.info("\nToken guardado/actualizado en 'token.json'. Autenticación completada.")
            except Exception as e:
                logger.error(f"\nError al guardar el token.json: {e}", exc_info=True)
                # No lanzamos la excepción para no detener la prueba, pero alertamos el error
                pass 
    else:
        logger.info("\nToken existente es válido. No se requiere refresco ni nueva autenticación.")
    
    return creds

if __name__ == '__main__':
    # Configuración básica si se ejecuta stand-alone (fuera del framework principal)
    if not logger.handlers:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger.info("\nEjecutando setup_gmail_api.py en modo stand-alone (sin config.py).")
        
    try:
        get_gmail_service_creds()
    except GmailSetupError as e:
        logger.critical(f"\nLa autenticación ha fallado: {e}")
    except Exception as e:
        logger.critical(f"\nError inesperado al ejecutar el setup: {e}", exc_info=True)