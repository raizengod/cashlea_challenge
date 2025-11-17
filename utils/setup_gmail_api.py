import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Define los scopes de acceso que solicitaste
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service_creds():
    """
    Realiza el flujo de autenticación para obtener o refrescar las credenciales.
    Genera el archivo token.json después de la primera autenticación exitosa.
    """
    creds = None
    # El archivo token.json almacena los tokens de acceso y refresco del usuario.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # Si no hay credenciales válidas disponibles, o el token ha expirado, autentica.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refrescando token...")
            creds.refresh(Request())
        else:
            print("Iniciando flujo de autenticación...")
            # El archivo credentials.json es el que descargaste de Google Cloud
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES
            )
            # Esto abrirá una ventana en tu navegador para que inicies sesión y des permiso
            creds = flow.run_local_server(port=0)

        # Guarda las credenciales para futuras ejecuciones
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            print("Token guardado en 'token.json'. Autenticación completada.")
    
    return creds

if __name__ == '__main__':
    get_gmail_service_creds()