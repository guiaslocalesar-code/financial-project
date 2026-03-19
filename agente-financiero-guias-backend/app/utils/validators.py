import re

def validate_cuit(cuit: str) -> bool:
    """
    Validates an Argentine CUIT/CUIL.
    Format: XX-XXXXXXXX-X or XXXXXXXXXXX
    """
    cuit = re.sub(r"[^0-9]", "", cuit)
    if len(cuit) != 11:
        return False
    
    base = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    total = 0
    for i in range(10):
        total += int(cuit[i]) * base[i]
    
    mod = total % 11
    digit = 11 - mod
    if digit == 11:
        digit = 0
    if digit == 10:
        digit = 9  # This case is rare but exists for some CUITs
        
    return int(cuit[10]) == digit

def validate_dni(dni: str) -> bool:
    """Validates a DNI (8 digits)."""
    dni = re.sub(r"[^0-9]", "", dni)
    return 7 <= len(dni) <= 9
