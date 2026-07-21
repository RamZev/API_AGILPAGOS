# app\routers\consultas_routers.py
from fastapi import APIRouter, HTTPException, status, Query, Path, Depends
from typing import Annotated, List

from app.services.consultas_service import ConsultasService
from app.dependencies import get_current_user
from app.models.consultas_models import (
	CVUInfo,
	SaldoResponse,
	MovimientoParams,
	MovimientosResponse,
	ConsultaCVUResponse
)


router = APIRouter(prefix="/consulta", tags=["Consultas"])


#-- Obtención de IdCuenta de la CVU. (6.1)
@router.get("/cvus", response_model=List[CVUInfo])
async def listar_cvus(id_usuario: str):
# async def listar_cvus(current_user: dict = Depends(get_current_user)):
	"""
	Obtiene la lista de CVU del usuario autenticado.
	
	Retorna todas las CVU asociadas al usuario con sus datos.
	"""
	try:
		# id_usuario = current_user.get("sub")
		if not id_usuario:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="ID de usuario no encontrado en el token"
			)
		
		cvus = await ConsultasService.listar_cvus(id_usuario)
		return cvus
		
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error al listar CVU: {str(e)}"
		)


#-- Consulta de Saldo. (6.2)
@router.get("/saldo/{id_cuenta}", response_model=SaldoResponse)
async def consultar_saldo(
	id_cuenta: str,
	# current_user: dict = Depends(get_current_user)
):
	"""
	Consulta el saldo de una CVU específica.
	
	Args:
	- id_cuenta: ID de la cuenta (GUID) obtenido de /cuentas/cvus
	"""
	try:
		saldo = await ConsultasService.consultar_saldo(id_cuenta)
		return saldo
		
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error al consultar saldo: {str(e)}"
		)


#-- Consulta de Movimientos. (6.3)
@router.get("/movimientos/{id_cuenta}", response_model=MovimientosResponse)
async def consultar_movimientos(
	id_cuenta: Annotated[str, Path()],
	params: Annotated[MovimientoParams, Query()]
	# current_user: dict = Depends(get_current_user)
):
	"""
	Consulta los movimientos de una CVU con paginación.
	
	Args:
	- id_cuenta: ID de la cuenta (GUID) obtenido de /cuentas/cvus
	- skip: Número de registros a saltar (paginación)
	- top: Cantidad de registros por página (máximo 100)
	- from_date: Fecha de inicio (opcional)
	- to_date: Fecha de fin (opcional)
	"""
	try:
		# id_usuario = current_user.get("sub")
		# if not id_usuario:
		# 	raise HTTPException(
		# 		status_code=status.HTTP_400_BAD_REQUEST,
		# 		detail="ID de usuario no encontrado en el token"
		# 	)
		
		movimientos = await ConsultasService.consultar_movimientos(
			id_cuenta=id_cuenta,
			parametros=params
		)
		
		return movimientos
		
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error al consultar movimientos: {str(e)}"
		)

#-- Consulta por CBU/CVU. (7.1)
@router.get("/cvu/{cvu}", response_model=ConsultaCVUResponse)
async def consultar_cvu(
	cvu: Annotated[str, Path()],
	# current_user: dict = Depends(get_current_user)
):
	"""
	Consulta los datos de una CVU específica.
	
	Args:
	- cvu: CBU/CVU a consultar
	"""
	try:
		cvu_info = await ConsultasService.consultar_cvu(cvu)
		
		if not cvu_info:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail=f"CVU {cvu} no encontrada"
			)
		
		return cvu_info
		
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error al consultar CVU: {str(e)}"
		)

#-- Consulta por CBU/CVU por Alias. (7.2)
@router.get("/cvu/alias/{alias}", response_model=ConsultaCVUResponse)
async def consultar_cvu_alias(
	alias: Annotated[str, Path()],
	# current_user: dict = Depends(get_current_user)
):
	"""
	Consulta los datos de una CVU específica por su alias.
	
	Args:
	- alias: Alias de la CVU a consultar
	"""
	try:
		cvu_info = await ConsultasService.consultar_cvu_alias(alias)
		
		if not cvu_info:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail=f"CVU {alias} no encontrada"
			)
		
		return cvu_info
		
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error al consultar CVU: {str(e)}"
		)