#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Mapeo entre números romanos y decimales para las secciones del Arancel.
"""

# Diccionario que mapea cada número romano a su equivalente decimal para las secciones
ROMAN_MAPPING = {
    'I': 1,
    'II': 2,
    'III': 3,
    'IV': 4,
    'V': 5,
    'VI': 6,
    'VII': 7,
    'VIII': 8,
    'IX': 9,
    'X': 10,
    'XI': 11,
    'XII': 12,
    'XIII': 13,
    'XIV': 14,
    'XV': 15,
    'XVI': 16,
    'XVII': 17,
    'XVIII': 18,
    'XIX': 19,
    'XX': 20,
    'XXI': 21
}

def roman_to_decimal(roman):
    """
    Convierte un número romano a decimal.
    
    Args:
        roman (str): Número romano (I, II, III, IV, etc.)
    
    Returns:
        int: Número decimal
    """
    # Para las secciones del Arancel, podemos usar directamente el mapeo
    roman = roman.strip().upper()
    if roman in ROMAN_MAPPING:
        return ROMAN_MAPPING[roman]
    
    # Para casos más generales, calculamos
    roman_values = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    decimal = 0
    prev_value = 0
    
    for char in reversed(roman):
        current_value = roman_values[char]
        if current_value >= prev_value:
            decimal += current_value
        else:
            decimal -= current_value
        prev_value = current_value
    
    return decimal

def print_mapping():
    """Imprime el mapeo entre números romanos y decimales para las secciones."""
    romans = list(ROMAN_MAPPING.keys())
    
    print("Mapeo de números romanos a decimales para las secciones del Arancel:")
    print("===================================================================")
    
    for roman in romans:
        decimal = ROMAN_MAPPING[roman]
        print(f"Sección {roman}: {decimal:02d}")

if __name__ == "__main__":
    print_mapping()
