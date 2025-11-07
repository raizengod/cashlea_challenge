from faker import Faker
import re
import random
import string

# Inicializa Faker. Usamos 'es_ES' para datos en español (opcional).
faker = Faker('es_ES')

class GeneradorDatos:
    """
    Clase que utiliza la librería Faker para generar datos de prueba:
    tanto válidos como inválidos, comúnmente requeridos en pruebas 
    de registro y login.
    """

    # --- Generación de Datos Válidos ---
    
    def generar_usuario_valido(self) -> dict:
        """
        Genera un conjunto completo de datos de usuario válidos (username, email, password).

        Returns:
            dict: Diccionario con las claves 'username', 'email' y 'password'.
        """        
        nombre = faker.first_name()
        apellido = faker.last_name()
        
        # 1. Genera el nombre de usuario de Faker, que puede contener caracteres especiales.
        username_raw = faker.user_name()
        # Filtra el nombre de usuario para que solo contenga caracteres alfanuméricos (letras y números).
        username_clean = re.sub(r'[^a-zA-Z0-9]', '', username_raw)
        # Combina el nombre de usuario limpio con un número aleatorio para asegurar unicidad.
        username = f"{username_clean}{faker.unique.random_int(min=100, max=999)}"
        
        # 2. Generar Email válido
        email = faker.email(safe=False)
        
        # 3. Generar Password válido (segura, 12 caracteres)
        password = faker.password(
            length=12, 
            special_chars=True, 
            digits=True, 
            upper_case=True, 
            lower_case=True
        )
        
        return {
            "username": username,
            "nombre": nombre,
            "apellido": apellido,
            "email": email,
            "password": password,
            "tipo_dato": "Válido"
        }

    # --- Generación de Datos Inválidos ---

    def generar_datos_invalidos(self) -> dict:
        """
        Genera un conjunto de datos de usuario intencionalmente inválidos.
        Útil para probar validaciones de formularios.

        Returns:
            dict: Diccionario con datos inválidos para 'username', 'email' y 'password'.
        """
        
        # 1. Username Inválido (Ej: Contiene espacios y un símbolo no permitido)
        # Esto fallará si el sistema solo acepta alfanuméricos y guiones/puntos.
        username_invalido = f"{faker.word()} {faker.word()}!"
        
        # 2. Email Inválido (Ej: No contiene el símbolo '@')
        # Tomamos un email normal y le quitamos el '@' y el dominio.
        email_base = faker.user_name()
        email_invalido = f"{email_base}dominio-invalido-com" # Falta el '@'
        
        # 3. Password Inválida (Ej: Contraseña muy corta)
        # La mayoría de los sistemas requieren al menos 8 caracteres.
        password_invalida = faker.password(length=random.randint(1, 4), special_chars=False)
        
        return {
            "username": username_invalido,
            "email": email_invalido,
            "password": password_invalida,
            "tipo_dato": "Inválido"
        }