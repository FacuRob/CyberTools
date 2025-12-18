import string
import secrets
import hashlib
from typing import Union, Dict

def generate_strong_password(
    length: int = 12, 
    phrase: str = None,
    use_numbers: bool = True,
    use_symbols: bool = True,
    use_uppercase: bool = True
) -> Union[str, ValueError]:
    """
    Genera contraseñas seguras de dos formas:
    1. Aleatoria tradicional (si no hay phrase)
    2. Basada en frase memorable (si hay phrase)
    
    Args:
        length (int): Longitud deseada (8-64 caracteres)
        phrase (str): Frase/oración para generar contraseña basada en ella
        use_numbers (bool): Incluir números
        use_symbols (bool): Incluir símbolos especiales
        use_uppercase (bool): Incluir mayúsculas
        
    Returns:
        str: Contraseña generada
        
    Raises:
        ValueError: Si los parámetros son inválidos
    
    Ejemplos:
        >>> generate_strong_password(12)
        'K#9mPqR!2xZw'
        
        >>> generate_strong_password(16, phrase="Me gusta programar en Python")
        'MgpeP3!7@hX9kL2'
    """
    # Validación
    if not isinstance(length, int):
        raise ValueError("La longitud debe ser un número entero")
    if not 8 <= length <= 64:
        raise ValueError("La longitud debe estar entre 8 y 64 caracteres")
    
    # Modo 1: Generación basada en frase
    if phrase:
        return _generate_from_phrase(phrase, length, use_numbers, use_symbols, use_uppercase)
    
    # Modo 2: Generación aleatoria tradicional
    return _generate_random(length, use_numbers, use_symbols, use_uppercase)


def _generate_from_phrase(
    phrase: str, 
    length: int,
    use_numbers: bool,
    use_symbols: bool,
    use_uppercase: bool
) -> str:
    """
    Genera contraseña basada en una frase memorable.
    Extrae iniciales y las mezcla con caracteres aleatorios.
    """
    if not phrase or not phrase.strip():
        raise ValueError("La frase no puede estar vacía")
    
    # Limpiar y procesar frase
    words = phrase.strip().split()
    if len(words) < 2:
        raise ValueError("La frase debe tener al menos 2 palabras")
    
    # Extraer iniciales (base de la contraseña)
    initials = ''.join(word[0] for word in words if word)
    
    # Hash de la frase para generación determinista pero segura
    phrase_hash = hashlib.sha256(phrase.encode()).hexdigest()
    
    # Construir caracteres disponibles
    chars = string.ascii_lowercase
    if use_uppercase:
        chars += string.ascii_uppercase
    if use_numbers:
        chars += string.digits
    if use_symbols:
        chars += "!@#$%&*"  # Símbolos seguros
    
    # Construir contraseña combinando iniciales con caracteres derivados
    password_parts = []
    
    # Usar iniciales (con mayúsculas según configuración)
    for i, char in enumerate(initials):
        if i < length // 2:  # Usar hasta la mitad de la longitud
            if use_uppercase and i % 2 == 0:
                password_parts.append(char.upper())
            else:
                password_parts.append(char.lower())
    
    # Completar con caracteres derivados del hash
    hash_index = 0
    while len(password_parts) < length:
        # Usar hash como semilla para selección pseudo-aleatoria
        char_pool = chars
        hash_byte = int(phrase_hash[hash_index % len(phrase_hash)], 16)
        
        # Seleccionar tipo de carácter según posición
        position = len(password_parts)
        
        if use_numbers and position % 4 == 1:
            # Cada 4 posiciones, intentar agregar número
            password_parts.append(str(hash_byte % 10))
        elif use_symbols and position % 6 == 2:
            # Cada 6 posiciones, intentar agregar símbolo
            symbols = "!@#$%&*"
            password_parts.append(symbols[hash_byte % len(symbols)])
        else:
            # Letra aleatoria basada en hash
            selected_char = char_pool[hash_byte % len(char_pool)]
            password_parts.append(selected_char)
        
        hash_index += 1
    
    # Mezclar usando el hash como semilla (reproducible pero seguro)
    seed_value = int(phrase_hash[:8], 16)
    shuffled = _deterministic_shuffle(password_parts, seed_value)
    
    return ''.join(shuffled[:length])


def _generate_random(
    length: int,
    use_numbers: bool,
    use_symbols: bool,
    use_uppercase: bool
) -> str:
    """
    Genera contraseña completamente aleatoria con secrets.
    """
    # Construir sets de caracteres según opciones
    char_sets = {'lowercase': string.ascii_lowercase}
    
    if use_uppercase:
        char_sets['uppercase'] = string.ascii_uppercase
    if use_numbers:
        char_sets['digits'] = string.digits
    if use_symbols:
        char_sets['symbols'] = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # Combinación de todos los caracteres
    all_chars = ''.join(char_sets.values())
    
    if not all_chars:
        raise ValueError("Debe seleccionar al menos un tipo de carácter")
    
    # Garantizar al menos un carácter de cada tipo seleccionado
    password_parts = []
    for char_set in char_sets.values():
        password_parts.append(secrets.choice(char_set))
    
    # Completar longitud restante
    remaining = length - len(password_parts)
    if remaining < 0:
        # Si la longitud es menor que tipos seleccionados
        password_parts = password_parts[:length]
    else:
        for _ in range(remaining):
            password_parts.append(secrets.choice(all_chars))
    
    # Mezclar aleatoriamente
    secrets.SystemRandom().shuffle(password_parts)
    
    return ''.join(password_parts)


def _deterministic_shuffle(items: list, seed: int) -> list:
    """Mezcla determinista usando semilla"""
    import random
    shuffled = items.copy()
    random.Random(seed).shuffle(shuffled)
    return shuffled


def analyze_password_strength(password: str) -> Dict[str, any]:
    """
    Analiza la fortaleza de una contraseña.
    
    Returns:
        Dict con métricas de seguridad
    """
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in string.punctuation for c in password)
    
    # Calcular pool de caracteres
    pool_size = 0
    if has_lower: pool_size += 26
    if has_upper: pool_size += 26
    if has_digit: pool_size += 10
    if has_symbol: pool_size += 32
    
    # Entropía (bits)
    import math
    entropy = len(password) * math.log2(pool_size) if pool_size > 0 else 0
    
    # Nivel de seguridad
    if entropy < 40:
        strength = "Débil"
    elif entropy < 60:
        strength = "Moderada"
    elif entropy < 80:
        strength = "Fuerte"
    else:
        strength = "Muy Fuerte"
    
    return {
        "length": len(password),
        "has_lowercase": has_lower,
        "has_uppercase": has_upper,
        "has_numbers": has_digit,
        "has_symbols": has_symbol,
        "entropy_bits": round(entropy, 2),
        "strength": strength,
        "pool_size": pool_size
    }


# Ejemplos de uso
if __name__ == "__main__":
    print("=== Contraseñas Aleatorias ===")
    print("Completa:", generate_strong_password(16))
    print("Sin símbolos:", generate_strong_password(16, use_symbols=False))
    print("Solo minúsculas y números:", generate_strong_password(12, use_uppercase=False, use_symbols=False))
    
    print("\n=== Contraseñas Basadas en Frases ===")
    phrase1 = "Me gusta programar en Python todos los dias"
    pwd1 = generate_strong_password(20, phrase=phrase1)
    print(f"Frase: '{phrase1}'")
    print(f"Contraseña: {pwd1}")
    print(f"Análisis: {analyze_password_strength(pwd1)}")
    
    phrase2 = "La seguridad es importante"
    pwd2 = generate_strong_password(16, phrase=phrase2, use_symbols=False)
    print(f"\nFrase: '{phrase2}'")
    print(f"Contraseña: {pwd2}")