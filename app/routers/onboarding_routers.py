# app\routers\onboarding_routers.py
from fastapi import APIRouter, HTTPException, status

from app.models.maestros_models import (
	DatosMaestrosResponse,
	Provincia,
	Nacionalidad,
	EstadoCivil,
	CondicionFiscal,
	Ocupacion,
	MotivoPEP
)
from app.models.onboarding_models import (
	UsuarioAltaRequest,
	UsuarioAltaResponse,
)
from app.core.exceptions import (
	AgilpagosValidationError,
	UsuarioYaExisteError
)
from app.services.onboarding_service import OnboardingService
from app.services.maestros_service import MaestrosService


router = APIRouter(prefix="/onboarding", tags=["Onboarding - Usuarios"])


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
		#-- Solicitar la creación del usuario en Agilpagos.
		response = await OnboardingService.crear_usuario(request)
		
		#-- Construir respuesta.
		return UsuarioAltaResponse(
			id_usuario=response.get("idUsuario", ""),
			cvu=response.get("cvu", ""),
			alias=response.get("alias", ""),
			id_usuario_entidad_lineas_cuentas=response.get("idUsuarioEntidadLineasCuentas", ""),
			numero_cuenta_entidad=request.numeroCuentaEntidad
		)
		
	except UsuarioYaExisteError as e:
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail=e.message
		)
	except AgilpagosValidationError as e:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=e.message
		)
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error al crear usuario: {str(e)}"
		)


@router.get("/usuario/{cuit}", response_model=UsuarioAltaResponse)
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


@router.get("/datos-maestros", response_model=DatosMaestrosResponse)
async def get_datos_maestros():
	"""
	Obtiene los datos maestros necesarios para el onboarding.
	
	Retorna:
	- Nacionalidades
	- Provincias
	- Estados Civiles
	- Condiciones Fiscales
	- Ocupaciones
	- Motivos PEP.
	"""
	try:
		return await MaestrosService.get_all()
		
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error al obtener datos maestros: {str(e)}"
		)