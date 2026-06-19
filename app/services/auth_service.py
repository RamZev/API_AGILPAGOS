# app/services/auth_service.py
"""Servicio de autenticación y gestión de tokens"""

from datetime import datetime, timedelta
from typing import Optional

from app.config import Config
from app.core.security import create_jwt_token, verify_jwt_token
from app.core.exceptions import TokenExpiredError, TokenInvalidError

def create_access_token(username: str, user_id: Optional[str] = None) -> str:
	"""
	Crea un token JWT interno para usuarios de la API Intermedia.
	
	Args:
		username: Nombre de usuario
		user_id: ID del usuario (opcional)
	
	Returns:
		Token JWT
	"""
	data = {"sub": username}
	if user_id:
		data["user_id"] = user_id
	
	return create_jwt_token(data)

def verify_access_token(token: str) -> dict:
	"""
	Verifica un token JWT interno.
	
	Args:
		token: Token JWT
	
	Returns:
		Payload del token
	
	Raises:
		TokenExpiredError: Si el token ha expirado
		TokenInvalidError: Si el token es inválido
	"""
	payload = verify_jwt_token(token)
	
	if not payload:
		raise TokenInvalidError("Token inválido o malformado")
	
	# Verificar expiración
	exp = payload.get("exp")
	if exp:
		exp_datetime = datetime.fromtimestamp(exp)
		if exp_datetime < datetime.utcnow():
			raise TokenExpiredError("Token ha expirado")
	
	return payload

def get_agilpagos_token() -> str:
	"""
	Obtiene un token de Agilpagos para usar en llamadas posteriores.
	El cliente HTTP maneja automáticamente la renovación.
	"""
	from app.core.http_client import agilpagos_client
	return agilpagos_client._get_token()