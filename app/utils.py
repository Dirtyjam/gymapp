import phonenumbers
import re

def validate_phone(phone_number):
    """Валидация и нормализация номера телефона (начинается с 7, без +)"""
    if not phone_number:
        return False, None

    # Удаляем все нецифровые символы
    digits = re.sub(r'\D', '', phone_number)

    # Преобразуем "8" в "7" (стандарт для России)
    if digits.startswith("8"):
        digits = "7" + digits[1:]

    # Добавим "7", если номер начинается, например, с 912...
    if len(digits) == 10:
        digits = "7" + digits

    # Проверка через phonenumbers
    try:
        parsed = phonenumbers.parse("+" + digits, "RU")
        if phonenumbers.is_valid_number(parsed):
            return True, digits  # без плюса, просто строка вида "7XXXXXXXXXX"
        else:
            return False, None
    except:
        return False, None
