# app\routers\test_routers.py
from fastapi import APIRouter
import httpx
import logging

from app.config import Config
from app.core.http_client import agilpagos_client
from app.core.security import generate_credentials
from app.models.auth_models import CredentialsRequest, GetTokenManualRequest


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/test", tags=["Test"])


@router.get("/")
async def root():
	return {
		"message": "API Gateway - Agilpagos",
		"version": "1.0.0",
		"environment": Config.ENVIRONMENT,
		"status": "operational",
		"docs": "/docs" if not Config.is_production() else None
	}


@router.get("/health")
async def health_check():
	"""Endpoint de verificación de salud"""
	health_status = {
		"status": "healthy",
		"environment": Config.ENVIRONMENT,
		"agilpagos_url": Config.AMBIENTE_BASE_URL,
		"agilpagos_connected": False
	}
	
	#-- Verificar conexión con Agilpagos.
	try:
		print("intenta tomar el token")
		await agilpagos_client._get_token()
		health_status["agilpagos_connected"] = True
		print("El token", agilpagos_client._token)
		print("El expiration", agilpagos_client._token_expiration)
	except Exception:
		health_status["agilpagos_connected"] = False
		if Config.is_production():
			health_status["status"] = "degraded"
	
	return health_status


@router.post("/get-credentials")
async def get_credentials(request: CredentialsRequest):
	"""
	Endpoint para obtener las credenciales requeridas para la solicitud del token Bearer en Agilpagos.
	Recibe username y password en el body (JSON) y retorna las credenciales hasheadas.
	"""
	creds = generate_credentials(
		username=request.username,
		password=request.password
	)
	return creds


@router.post("/get-token")
async def get_token_manual(request: GetTokenManualRequest):
	"""
	Endpoint para obtener el token Bearer de Agilpagos de forma MANUAL.
	
	DEBE recibir los datos EXACTAMENTE como los devuelve /get-credentials:
	- userName: el email/username
	- password: el password hasheado (NO el texto plano)
	- nonce: el nonce generado
	- created: la fecha en formato ISO
	
	Útil para probar manualmente el flujo de autenticación.
	"""
	try:
		#-- 1. Preparar payload para Agilpagos.
		payload = {
			"idEntidad": request.idEntidad,
			"userName": request.userName,
			"password": request.password,  #-- Ya está hasheado.
			"nonce": request.nonce,
			"created": request.created
		}
		
		#-- Agregar cuit si viene.
		if request.cuit:
			payload["cuit"] = request.cuit
		
		#-- 2. Llamar a Agilpagos.
		url = f"{Config.AMBIENTE_BASE_URL}/Account/Login"
		
		async with httpx.AsyncClient(timeout=30.0) as client:
			response = await client.post(url, json=payload)
			response.raise_for_status()
			data = response.json()
			
			#-- 3. Devolver el token y metadatos.
			return {
				"status": "success",
				"status_code": response.status_code,
				"token": data.get("token"),
				"expiration": data.get("expiration"),
				"refreshToken": data.get("refreshToken"),
				"issued": data.get("issued")
			}
			
	except httpx.HTTPStatusError as e:
		return {
			"status": "error",
			"status_code": e.response.status_code,
			"message": "Error al obtener token de Agilpagos",
			"detail": e.response.text,
			"url": str(e.request.url)
		}
	except Exception as e:
		return {
			"status": "error",
			"status_code": 500,
			"message": "Error inesperado",
			"detail": str(e)
		}
