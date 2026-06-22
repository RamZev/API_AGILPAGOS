# app/utils/validators.py
"""Funciones de validación"""

import re
from datetime import date


def validate_cuit(cuit: str) -> bool:
	"""
	Valida que un CUIT tenga formato válido (11 dígitos).
	
	Args:
		cuit: CUIT a validar
		
	Returns:
		True si es válido, False en caso contrario
	"""
	return bool(re.match(r'^[0-9]{11}$', cuit))


def validate_email(email: str) -> bool:
	"""
	Valida que un email tenga formato válido.
	
	Args:
		email: Email a validar
		
	Returns:
		True si es válido, False en caso contrario
	"""
	pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
	return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
	"""
	Valida que un teléfono tenga formato válido (solo dígitos).
	
	Args:
		phone: Teléfono a validar
		
	Returns:
		True si es válido, False en caso contrario
	"""
	return bool(re.match(r'^[0-9]+$', phone))


def validate_age(birth_date: date) -> bool:
	"""
	Valida que la edad esté entre 13 y 100 años.
	
	Args:
		birth_date: Fecha de nacimiento
		
	Returns:
		True si la edad es válida, False en caso contrario
	"""
	today = date.today()
	age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
	return 13 <= age <= 100


def validate_alias(alias: str) -> bool:
	"""
	Valida que un alias tenga formato válido.
	
	Args:
		alias: Alias a validar
		
	Returns:
		True si es válido, False en caso contrario
	"""
	#-- Longitud: entre 6 y 20 caracteres.
	if not 6 <= len(alias) <= 20:
		return False
	
	#-- Caracteres permitidos: letras, números, puntos y guiones.
	pattern = r'^[A-Za-z0-9.-]+$'
	return bool(re.match(pattern, alias))