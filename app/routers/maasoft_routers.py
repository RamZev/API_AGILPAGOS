# app\routers\maasoft_routers.py
from fastapi import APIRouter, HTTPException, status
import httpx
# import logging

from app.config import Config
from app.models.maasoft_models import SocioResponse
from app.services.maasoft_service import MaaSoftService
# from app.dependencies


# logger = logging.getLogger(__name__)
router = APIRouter(prefix="/maasoft", tags=["API - MAASoft"])


@router.get("/socio/{cuit}", response_model=SocioResponse)
async def get_socio_cuit(
	cuit: int,
	# current_user: dict = Depends(get_current_user)  # Protegido con JWT,
):
	"""
	Obtiene los datos de un socio de MaaSoft por su CUIT.
	
	Args:
		cuit: CUIT del socio (ej: 12345678912)
	
	Returns:
		Datos completos del socio
	"""
	try:
		socio = await MaaSoftService.get_socio_cuit(cuit)
		if not socio:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail=f"No se encontró socio con CUIT {cuit}"
			)
		return socio
	
	except httpx.HTTPStatusError as e:
		if e.response.status_code == 404:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail=f"No se encontró socio con CUIT {cuit}"
			)
		elif e.response.status_code >= 500:
			raise HTTPException(
				status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
				detail=f"Error en el servidor de MaaSoft: {e.response.text}"
			)
		else:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail=f"Error al consultar MaaSoft: {e.response.text}"
			)
			
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error inesperado al consultar socio: {str(e)}"
		)


@router.get("/sociocodigo/{codigo}", response_model=SocioResponse)
async def get_socio_codigo(
	codigo: int,
	# current_user: dict = Depends(get_current_user)  # Protegido con JWT,
):
	"""
	Obtiene los datos de un socio de MaaSoft por su CÓDIGO.
	
	Args:
		codigo: Código del socio (ej: 1234)
	
	Returns:
		Datos completos del socio
	"""
	try:
		socio = await MaaSoftService.get_socio_codigo(codigo)
		if not socio:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail=f"No se encontró socio con Código {codigo}"
			)
		return socio
	
	except httpx.HTTPStatusError as e:
		if e.response.status_code == 404:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail=f"No se encontró socio con Código {codigo}"
			)
		elif e.response.status_code >= 500:
			raise HTTPException(
				status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
				detail=f"Error en el servidor de MaaSoft: {e.response.text}"
			)
		else:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail=f"Error al consultar MaaSoft: {e.response.text}"
			)
			
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error inesperado al consultar socio: {str(e)}"
		)


@router.get("/socio/verificar/{cuit}")
async def verificar_socio(
	cuit: int,
	# current_user: dict = Depends(get_current_user)
):
	"""
	Verifica si un socio existe en MaaSoft.
	
	Args:
		cuit: CUIT del socio
	
	Returns:
		{"existe": True/False}
	"""
	try:
		existe = await MaaSoftService.existe_socio(cuit)
		return {"existe": existe, "cuit": cuit}
		
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error al verificar socio: {str(e)}"
		)