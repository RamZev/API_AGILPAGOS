# app/dependencies.py
"""Dependencias para FastAPI"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from app.services.auth_service import verify_access_token
from app.core.exceptions import TokenExpiredError, TokenInvalidError

security = HTTPBearer()


async def get_current_user(
	credentials: HTTPAuthorizationCredentials = Depends(security)
):
	"""
	Dependencia para proteger endpoints.
	Valida el token JWT interno.
	"""
	token = credentials.credentials
	
	try:
		payload = verify_access_token(token)
		return payload
	except TokenExpiredError:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Token expirado",
			headers={"WWW-Authenticate": "Bearer"},
		)
	except TokenInvalidError:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Token inválido",
			headers={"WWW-Authenticate": "Bearer"},
		)


async def get_optional_user(
	credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
	"""
	Dependencia opcional para endpoints que pueden o no requerir autenticación.
	"""
	if not credentials:
		return None
	
	try:
		return await get_current_user(credentials)
	except HTTPException:
		return None