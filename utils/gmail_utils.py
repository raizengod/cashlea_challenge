import base64
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    """Retorna el objeto de servicio de la Gmail API, manejando la autenticación."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # Esto es una comprobación para asegurar que el token se refresque si es necesario.
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    # Construye y retorna el servicio de la API
    service = build('gmail', 'v1', credentials=creds)
    return service

def find_email(subject_line, sender_email, wait_timeout=30):
    """
    Busca un email por asunto y remitente en la bandeja de entrada.
    
    :param subject_line: El texto esperado en el asunto.
    :param sender_email: El email del remitente (ej: 'support@midominio.com').
    :param wait_timeout: Tiempo máximo de espera en segundos.
    :return: El cuerpo del email encontrado o None.
    """
    service = get_gmail_service()
    query = f"subject:\"{subject_line}\" from:{sender_email}"
    
    # Lógica de reintento para esperar que el email llegue
    import time
    start_time = time.time()
    
    while time.time() - start_time < wait_timeout:
        try:
            # Llama a la API para obtener una lista de IDs de mensajes
            response = service.users().messages().list(userId='me', q=query, maxResults=1).execute()
            messages = response.get('messages', [])
            
            if messages:
                # Obtiene el primer mensaje que coincide
                msg = service.users().messages().get(userId='me', id=messages[0]['id'], format='full').execute()
                
                # Procesa el cuerpo del mensaje
                # La estructura del cuerpo puede variar (parts, body, etc.)
                # Aquí se intenta obtener la parte de texto/html
                for part in msg['payload']['parts']:
                    if part['mimeType'] == 'text/html' and 'data' in part['body']:
                        # El cuerpo está codificado en Base64 URL Safe
                        data = part['body']['data']
                        decoded_body = base64.urlsafe_b64decode(data).decode('utf-8')
                        return decoded_body
                    
                # Si no se encontró un cuerpo HTML, retorna el objeto completo o un error
                return "Email encontrado, pero no se pudo decodificar el cuerpo HTML."
                
        except Exception as e:
            print(f"Error al buscar email: {e}")
            pass # Continúa el bucle de espera en caso de error temporal o email no encontrado

        print("Email no encontrado. Reintentando en 5 segundos...")
        time.sleep(5)
        
    return None