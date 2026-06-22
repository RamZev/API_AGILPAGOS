# app/routers/auth.py
from fastapi import APIRouter, HTTPException, status

from app.models.auth import LoginRequest, LoginResponse
from app.services.auth_service import create_access_token, verify_access_token
from app.core.http_client import agilpagos_client

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
	"""
	Autentica a un usuario en la API Intermedia.
	Genera un token JWT interno para consumir los endpoints protegidos.
	"""
	# Aquí validarías las credenciales contra tu base de datos de usuarios
	# Por ahora, aceptamos cualquier credencial (para desarrollo)
	
	#-- Verificar que el cliente HTTP pueda obtener token de Agilpagos.
	try:
		agilpagos_client._get_token()
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
			detail=f"No se pudo conectar con Agilpagos: {str(e)}"
		)
	
	#-- Crear token JWT interno.
	access_token = create_access_token(
		username=request.username
	)
	
	return LoginResponse(
		access_token=access_token,
		expires_in=1800  #-- 30 minutos.
	)


@router.get("/verify")
async def verify_token_status(token: str):
	"""Verifica si un token JWT es válido (para pruebas)"""
	try:
		payload = verify_access_token(token)
		return {"valid": True, "payload": payload}
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail=f"Token inválido o expirado: {str(e)}"
		)