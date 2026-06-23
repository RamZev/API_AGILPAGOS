# app\routers\maestros.py
from fastapi import APIRouter, HTTPException, status

from app.services.maestros_service import MaestrosService
from app.dependencies import get_current_user
from app.models.maestros import DatosMaestrosResponse


router = APIRouter(prefix="/maestros", tags=["Datos Maestros"])


@router.get("/nacionalidades")
async def get_nacionalidades():
	"""
	Obtiene el listado de nacionalidades disponibles.
	"""
	try:
		return await MaestrosService.get_nacionalidades()
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error al obtener nacionalidades: {str(e)}"
		)


@router.get("/provincias")
async def get_provincias():
	"""
	Obtiene el listado de provincias argentinas.
	"""
	try:
		return await MaestrosService.get_provincias()
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error al obtener provincias: {str(e)}"
		)


@router.get("/estados-civiles")
async def get_estados_civiles():
	"""
	Obtiene el listado de estados civiles.
	"""
	try:
		return await MaestrosService.get_estados_civiles()
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error al obtener estados civiles: {str(e)}"
		)


@router.get("/condiciones-fiscales")
async def get_condiciones_fiscales():
	"""
	Obtiene el listado de condiciones fiscales.
	"""
	try:
		return await MaestrosService.get_condiciones_fiscales()
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error al obtener condiciones fiscales: {str(e)}"
		)


@router.get("/ocupaciones")
async def get_ocupaciones():
	"""
	Obtiene el listado de ocupaciones.
	"""
	try:
		return await MaestrosService.get_ocupaciones()
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error al obtener ocupaciones: {str(e)}"
		)


@router.get("/motivos-pep")
async def get_motivos_pep():
	"""
	Obtiene el listado de motivos para Personas Expuestas Políticamente.
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
	Útil para cargar formularios completos de onboarding.
	"""
	try:
		datos = await MaestrosService.get_all()
		return datos
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error al obtener datos maestros: {str(e)}"
		)