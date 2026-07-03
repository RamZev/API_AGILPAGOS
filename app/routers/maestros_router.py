# app\routers\maestros_router.py
from fastapi import APIRouter, HTTPException, status

from app.services.maestros_service import MaestrosService
from app.dependencies import get_current_user
from app.models.maestros_models import (
	DatosMaestrosResponse,
	Nacionalidad,
	Provincia,
	EstadoCivil,
	CondicionFiscal,
	Ocupacion,
	MotivoPEP
)


router = APIRouter(prefix="/maestros", tags=["Datos Maestros"])


@router.get("/nacionalidades", response_model=Nacionalidad)
async def get_nacionalidades():
	"""
	Obtiene el listado de Nacionalidades disponibles.
	"""
	try:
		return await MaestrosService.get_nacionalidades()
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error al obtener nacionalidades: {str(e)}"
		)


@router.get("/provincias", response_model=list[Provincia])
async def get_provincias():
	"""
	Obtiene el listado de Provincias Argentinas.
	"""
	try:
		return await MaestrosService.get_provincias()
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error al obtener provincias: {str(e)}"
		)
	

@router.get("/estados-civiles", response_model=list[EstadoCivil])
async def get_estados_civiles():
	"""
	Obtiene el listado de Estados Civiles.
	"""
	try:
		return await MaestrosService.get_estados_civiles()
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error al obtener estados civiles: {str(e)}"
		)


@router.get("/condiciones-fiscales", response_model=list[CondicionFiscal])
async def get_condiciones_fiscales():
	"""
	Obtiene el listado de Condiciones Fiscales.
	"""
	try:
		return await MaestrosService.get_condiciones_fiscales()
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error al obtener condiciones fiscales: {str(e)}"
		)


@router.get("/ocupaciones", response_model=list[Ocupacion])
async def get_ocupaciones():
	"""
	Obtiene el listado de Ocupaciones.
	"""
	try:
		return await MaestrosService.get_ocupaciones()
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error al obtener ocupaciones: {str(e)}"
		)


@router.get("/motivos-pep", response_model=list[MotivoPEP])
async def get_motivos_pep():
	"""
	Obtiene el listado de Motivos para Personas Expuestas Políticamente (PEP).
	"""
	try:
		return await MaestrosService.get_motivos_pep()
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error al obtener motivos PEP: {str(e)}"
		)


@router.get("/todos", response_model=DatosMaestrosResponse)
async def get_todos_los_datos_maestros():
	"""
	Obtiene todos los datos maestros en una sola llamada.
	Útil para cargar formularios completos de OnBoarding.
	"""
	try:
		datos = await MaestrosService.get_all()
		return datos
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error al obtener datos maestros: {str(e)}"
		)