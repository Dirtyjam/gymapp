import phonenumbers
from flask import jsonify
from functools import wraps
from flask import request


def validate_phone(phone_number):
    """Валидация и нормализация номера телефона"""
    try:
        parsed = phonenumbers.parse(phone_number, 'RU')
        if phonenumbers.is_valid_number(parsed):
            normalized = phonenumbers.format_number(
                parsed, phonenumbers.PhoneNumberFormat.E164
            )
            return True, normalized
        return False, None
    except:
        return False, None
