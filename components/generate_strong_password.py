import string
import random
import secrets
from typing import Union

def generate_strong_password(length: int = 12) -> Union[str, ValueError]:
    """
    Genera una contraseña aleatoria y segura de la longitud especificada.
    
    Args:
        length (int): Longitud deseada de la contraseña (entre 8 y 64 caracteres).
        
    Returns:
        str: Contraseña generada o mensaje de error si la longitud no es válida.
        
    Raises:
        ValueError: Si la longitud no está en el rango permitido.
    
    Características:
        - Usa el módulo secrets para mayor seguridad criptográfica
        - Garantiza al menos un carácter de cada tipo (minúscula, mayúscula, dígito, símbolo)
        - Proporciona una distribución más equilibrada de tipos de caracteres
        - Validación mejorada de parámetros
        - Tipado estático con type hints
        - Documentación mejorada
    """
    # Validación de parámetros
    if not isinstance(length, int):
        raise ValueError("La longitud debe ser un número entero")
    if not 8 <= length <= 64:
        raise ValueError("La longitud debe estar entre 8 y 64 caracteres")

    # Conjuntos de caracteres
    char_sets = {
        'lowercase': string.ascii_lowercase,
        'uppercase': string.ascii_uppercase,
        'digits': string.digits,
        'punctuation': string.punctuation
    }
    
    # Combinación de todos los caracteres
    all_chars = ''.join(char_sets.values())
    
    # Garantizamos al menos un carácter de cada tipo
    password_parts = [
        secrets.choice(char_sets['lowercase']),
        secrets.choice(char_sets['uppercase']),
        secrets.choice(char_sets['digits']),
        secrets.choice(char_sets['punctuation'])
    ]
    
    # Si la longitud es exactamente 4, ya tenemos la contraseña
    if length == 4:
        random.shuffle(password_parts)
        return ''.join(password_parts)
    
    # Generamos el resto de la contraseña con distribución equilibrada
    remaining_length = length - 4
    remaining_chars = []
    
    # Distribución más equilibrada para el resto de caracteres
    for _ in range(remaining_length):
        char_set_name = secrets.choice(list(char_sets.keys()))
        remaining_chars.append(secrets.choice(char_sets[char_set_name]))
    
    # Combinamos y mezclamos
    password_chars = password_parts + remaining_chars
    random.shuffle(password_chars)
    
    return ''.join(password_chars)


# Ejemplo de uso
if __name__ == "__main__":
    try:
        print("Contraseña de 12 caracteres:", generate_strong_password())
        print("Contraseña de 16 caracteres:", generate_strong_password(16))
        print("Contraseña de 8 caracteres:", generate_strong_password(8))
    except ValueError as e:
        print(f"Error: {e}")