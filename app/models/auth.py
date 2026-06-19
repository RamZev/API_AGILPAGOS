from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
	"""Solicitud de login (para usuarios de la API Intermedia)"""
	username: str
	password: str

class LoginResponse(BaseModel):
	"""Respuesta de login"""
	access_token: str
	token_type: str = "bearer"
	expires_in: int

class TokenData(BaseModel):
	"""Datos del token JWT interno"""
	username: str
	user_id: Optional[str] = None