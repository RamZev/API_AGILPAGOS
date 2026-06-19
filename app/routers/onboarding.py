# app/routers/onboarding.py
from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any

from app.models.onboarding import (
	UsuarioAltaRequest,
	UsuarioAltaResponse,
	UsuarioConsultaResponse,
	ErrorResponse
)
from app.services.onboarding_service import OnboardingService
from app.dependencies import get_current_user
from app.core.http_client import agilpagos_client  # <--- ¡AGREGAR ESTA IMPORTACIÓN!

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])

@router.post("/usuario", response_model=UsuarioAltaResponse)
async def crear_usuario(
	request: UsuarioAltaRequest,
	# current_user: dict = Depends(get_current_user)  # Protegido
):
	"""
	Crea un nuevo usuario y su CVU en Agilpagos.
	
	- Valida que el usuario sea mayor de 13 años
	- Verifica que el CUIT no esté duplicado
	- Crea el usuario y su CVU
	- Retorna los datos de la cuenta creada
	"""
	try:
		# 1. Validar datos (ya lo hace Pydantic)
		
		# 2. Verificar si el usuario ya existe
		usuario_existente = await OnboardingService.verificar_usuario_existe(
			request.cuit
		)
		
		if usuario_existente:
			cvus = usuario_existente.get("cvus", [])
			if cvus:
				raise HTTPException(
					status_code=status.HTTP_409_CONFLICT,
					detail=f"El usuario con CUIT {request.cuit} ya tiene {len(cvus)} CVU(s) activas"
				)
		
		# 3. Crear usuario en Agilpagos
		response = await OnboardingService.crear_usuario(request)
		
		# 4. Construir respuesta
		return UsuarioAltaResponse(
			id_usuario=response.get("idUsuario"),
			cvu=response.get("cvu"),
			alias=response.get("alias", ""),
			id_usuario_entidad_lineas_cuentas=response.get("idUsuarioEntidadLineasCuentas"),
			numero_cuenta_entidad=request.numeroCuentaEntidad
		)
		
	except ValueError as e:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=str(e)
		)
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error al crear usuario: {str(e)}"
		)

@router.get("/usuario/{cuit}")
async def consultar_usuario(cuit: str):
	"""
	Consulta un usuario por su CUIT.
	Retorna los datos del usuario y sus CVU asociadas.
	"""
	try:
		usuario = await OnboardingService.verificar_usuario_existe(cuit)
		
		if not usuario:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail=f"Usuario con CUIT {cuit} no encontrado"
			)
		
		return usuario
		
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error al consultar usuario: {str(e)}"
		)

@router.get("/datos-maestros")
async def get_datos_maestros():
	"""
	Obtiene los datos maestros necesarios para el onboarding.
	Retorna: nacionalidades, provincias, estados civiles, condiciones fiscales,
	ocupaciones y motivos PEP.
	"""
	try:
		# Agrupar las llamadas a Agilpagos
		endpoints = {
			"nacionalidades": "/OnBoarding/Nacionalidades",
			"provincias": "/OnBoarding/Provincias/País/AC98A1E7-CF65-4430-BF16-24439F35853B",
			"estados_civiles": "/OnBoarding/EstadoCivil",
			"condiciones_fiscales": "/OnBoarding/CondicionesFiscales",
			"ocupaciones": "/OnBoarding/Ocupaciones",
			"motivos_pep": "/OnBoarding/MotivosPEP"
		}
		
		result = {}
		for key, endpoint in endpoints.items():
			try:
				# ¡USAR await PORQUE ES ASÍNCRONO!
				result[key] = await agilpagos_client.request("GET", endpoint)
			except Exception as e:
				result[key] = {"error": str(e)}
		
		return result
		
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error al obtener datos maestros: {str(e)}"
		)