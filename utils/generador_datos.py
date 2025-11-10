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
    de registro, login, formularios y entradas de datos.
    """

    # --- Generación de Datos Válidos (Original) ---
    
    def generar_usuario_valido(self) -> dict:
        """
        Genera un conjunto completo de datos de usuario válidos (username, email, password, confirmar_password).

        Returns:
            dict: Diccionario con las claves 'username', 'email', 'password' y 'confirmar_password'.
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
        
        # Confirmar_password debe ser igual a password para ser válido
        confirmar_password = password
        
        return {
            "username": username,
            "nombre": nombre,
            "apellido": apellido,
            "email": email,
            "password": password,
            "confirmar_password": confirmar_password,
            "tipo_dato": "Válido"
        }

    # --- Generación de Datos Inválidos (Original) ---

    def generar_datos_invalidos(self) -> dict:
        """
        Genera un conjunto de datos de usuario intencionalmente inválidos.
        Útil para probar validaciones de formularios, incluyendo la discrepancia de contraseñas.

        Returns:
            dict: Diccionario con datos inválidos para 'username', 'email', 'password' y 'confirmar_password'.
        """
        
        # 1. Username Inválido (Ej: Contiene espacios y un símbolo no permitido)
        username_invalido = f"{faker.word()} {faker.word()}!"
        
        # 2. Email Inválido (Ej: No contiene el símbolo '@')
        email_base = faker.user_name()
        email_invalido = f"{email_base}dominio-invalido-com" # Falta el '@'
        
        # 3. Password Inválida (Ej: Contraseña muy corta)
        password_invalida = faker.password(length=random.randint(1, 4), special_chars=False)
        
        # Confirmar_password debe ser diferente a password
        # Generamos una contraseña fuerte que no coincida para forzar el fallo de validación
        password_diferente = self.generar_password_segura(longitud=12) 
        
        return {
            "username": username_invalido,
            "email": email_invalido,
            "password": password_invalida,
            "confirmar_password": password_diferente,
            "tipo_dato": "Inválido"
        }

    # --- Nuevos Métodos de Generación Específica ---
    
    def generar_numero_aleatorio(self, digitos: int = 5) -> int:
        """
        Genera un número entero aleatorio.

        Args:
            digitos (int): La cantidad de dígitos que tendrá el número.

        Returns:
            int: Un número entero aleatorio.
        """
        # Genera un número de 5 dígitos (o la cantidad especificada)
        return faker.random_int(min=10**(digitos-1), max=(10**digitos)-1)

    def generar_palabra_corta(self) -> str:
        """
        Genera una cadena de texto simple, alfanumérica y corta.
        Ideal para campos de entrada de texto cortos (ej. nombres, campos alfabéticos).

        Returns:
            str: Una cadena de texto con un máximo de 20 caracteres.
        """
        # Usamos faker.text(max_nb_chars=20) para generar texto aleatorio 
        # y nos aseguramos de que no tenga el punto final ni espacios innecesarios.
        return faker.text(max_nb_chars=20).replace('.', '').strip()
        
    def generar_fecha_nacimiento(self, formato: str = "%Y-%m-%d") -> str:
        """
        Genera una fecha de nacimiento válida (entre 18 y 65 años atrás).

        Args:
            formato (str): El formato de salida de la fecha (ej. "AAAA-MM-DD").

        Returns:
            str: Una fecha de nacimiento formateada.
        """
        # Genera una fecha en el pasado, asegurando que la persona tenga entre 18 y 65 años.
        return faker.date_of_birth(minimum_age=1, maximum_age=2000).strftime(formato)
        
    def generar_password_segura(self, longitud: int = 12) -> str:
        """
        Genera una contraseña fuerte que cumple con requisitos comunes (mayúsculas, minúsculas, dígitos, especial).

        Args:
            longitud (int): Longitud deseada de la contraseña.

        Returns:
            str: Una contraseña fuerte.
        """
        return faker.password(
            length=longitud, 
            special_chars=True, 
            digits=True, 
            upper_case=True, 
            lower_case=True
        )