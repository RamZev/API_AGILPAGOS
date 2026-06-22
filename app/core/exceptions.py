# app/core/exceptions.py
"""Excepciones personalizadas para la API"""


class AgilpagosAPIError(Exception):
	"""Error general al interactuar con la API de Agilpagos"""
	def __init__(self, message: str, status_code: int = 0, response: dict = {}):
		self.message = message
		self.status_code = status_code
		self.response = response
		super().__init__(self.message)


class AgilpagosAuthError(AgilpagosAPIError):
	"""Error de autenticación con Agilpagos"""
	pass


class AgilpagosNotFoundError(AgilpagosAPIError):
	"""Recurso no encontrado en Agilpagos"""
	pass


class AgilpagosValidationError(AgilpagosAPIError):
	"""Error de validación al enviar datos a Agilpagos"""
	pass


class TokenExpiredError(Exception):
	"""Token interno expirado"""
	pass


class TokenInvalidError(Exception):
	"""Token interno inválido"""
	pass