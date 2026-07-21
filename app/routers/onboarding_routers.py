# app\routers\onboarding_routers.py
from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import Annotated

from app.models.maestros_models import DatosMaestrosResponse
from app.models.onboarding_models import (
	UsuarioAltaRequest,
	UsuarioAltaResponse,
	UsuarioConsultaResponse,
	BajaCVURequest,
	BajaCVUResponse,
	AliasChangeRequest
)
from app.core.exceptions import (
	AgilpagosValidationError,
	UsuarioYaExisteError
)
from app.services.onboarding_service import OnboardingService
from app.services.maestros_service import MaestrosService


router = APIRouter(prefix="/onboarding", tags=["Onboarding - Usuarios"])


#-- Obtener Datos Maestros para Onboarding. (3.0)
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


#-- Alta de Usuario y CVU. (3.1)
@router.post("/usuario/alta", response_model=UsuarioAltaResponse)
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


#-- Consulta de CVU y Alias por CUIT. (3.1.1)
@router.get("/usuario/consulta/{cuit}", response_model=UsuarioConsultaResponse)
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
	
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error al consultar usuario: {str(e)}"
		)


#-- Baja de CVU ante COELSA (eliminación definitiva). (3.3.2)
@router.delete("/cvu/baja", response_model=BajaCVUResponse)
async def baja_cvu(
	request: BajaCVURequest,
	id_usuario: Annotated[str, Query(description="ID del usuario (GUID)")],
	# current_user: dict = Depends(get_current_user)  # Descomentar en producción
):
	"""
	Da de baja una CVU ante Coelsa (eliminación definitiva).
	
	⚠️ ADVERTENCIA: Esta acción es irreversible. La CVU no podrá ser recuperada.
	
	Requisitos:
	- La CVU debe pertenecer al usuario
	- La CVU debe tener saldo cero (según documentación de Agilpagos)
	- Se debe enviar el motivo de baja (GUID fijo)
	
	Args:
		request: Datos de la solicitud (cvu, idMotivoBaja, observaciones)
		id_usuario: ID del usuario (GUID) para el header IDWEBUSUARIOFINAL
	"""
	try:
		# 1. Verificar que el usuario esté autenticado
		# if not current_user:
		#     raise HTTPException(
		#         status_code=status.HTTP_401_UNAUTHORIZED,
		#         detail="Usuario no autenticado"
		#     )
		
		# 2. Verificar que la CVU pertenezca al usuario (opcional pero recomendado)
		es_propietario = await OnboardingService.verificar_cvu_pertenece_usuario(
			request.cvu,
			id_usuario
		)
		
		if not es_propietario:
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail=f"La CVU {request.cvu} no pertenece al usuario especificado"
			)
		
		# 3. Ejecutar la baja
		await OnboardingService.baja_cvu(request, id_usuario)
		
		# 4. Retornar respuesta exitosa
		return BajaCVUResponse(
			success=True,
			message=f"CVU {request.cvu} dada de baja exitosamente",
			cvu=request.cvu
		)
		
	except AgilpagosValidationError as e:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=str(e)
		)
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error al dar de baja la CVU: {str(e)}"
		)


#-- Asignación/Cambio de Alias. (3.2)
@router.put("/alias/cambiar")
async def cambiar_alias(
	id_usuario: Annotated[str, Query()],
	request: AliasChangeRequest,
	# current_user: dict = Depends(get_current_user)
):
	"""
	Cambia el alias de una CVU.
	
	Validaciones (realizadas en el modelo):
	- El alias debe tener entre 6 y 20 caracteres
	- Solo puede contener letras, números, puntos y guiones
	- Deben pasar al menos 24 horas entre cambios (según fecha_ultimo_cambio enviada)
	"""
	try:
		# id_usuario = current_user.get("sub")
		# if not id_usuario:
		# 	raise HTTPException(
		# 		status_code=status.HTTP_400_BAD_REQUEST,
		# 		detail="ID de usuario no encontrado en el token"
		# 	)
		
		#-- El modelo ya validó todo, solo llama al servicio.
		resultado = await OnboardingService.cambiar_alias(
			cvu=request.cvu,
			nuevo_alias=request.nuevo_alias,
			id_usuario=id_usuario
		)
		print(f"Resultado (Router): {resultado}")
		return {
			"success": True,
			"message": f"Alias cambiado exitosamente a '{request.nuevo_alias}'",
			# "cvu": request.cvu,
			# "nuevo_alias": request.nuevo_alias,
			# "fecha_cambio": datetime.now().isoformat()  # Para que el cliente actualice su BD
		}
	
	except AgilpagosValidationError as e:
		#-- Error de Agilpagos.
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=str(e)
		)
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error al cambiar alias: {str(e)}"
		)