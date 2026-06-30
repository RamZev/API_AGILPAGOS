# app/routers/cuentas.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from datetime import datetime

from app.services.cuentas_service import CuentasService
from app.dependencies import get_current_user
from app.models.cuentas import CVUInfo, SaldoResponse, MovimientosResponse

router = APIRouter(prefix="/cuentas", tags=["Cuentas"])


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
		
		cvus = await CuentasService.listar_cvus(id_usuario)
		return cvus
		
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error al listar CVU: {str(e)}"
		)


@router.get("/saldo/{id_cuenta}", response_model=SaldoResponse)
async def consultar_saldo(
	id_cuenta: str,
	current_user: dict = Depends(get_current_user)
):
	"""
	Consulta el saldo de una CVU específica.
	
	Args:
		id_cuenta: ID de la cuenta (GUID) obtenido de /cuentas/cvus
	"""
	try:
		saldo = await CuentasService.consultar_saldo(id_cuenta)
		return saldo
		
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error al consultar saldo: {str(e)}"
		)


@router.get("/movimientos/{id_cuenta}", response_model=MovimientosResponse)
async def consultar_movimientos(
	id_cuenta: str,
	skip: int = Query(0, ge=0, description="Número de registros a saltar"),
	top: int = Query(10, ge=1, le=100, description="Registros por página"),
	from_date: Optional[datetime] = Query(None, description="Fecha de inicio (ISO)"),
	to_date: Optional[datetime] = Query(None, description="Fecha de fin (ISO)"),
	current_user: dict = Depends(get_current_user)
):
	"""
	Consulta los movimientos de una CVU con paginación.
	
	Args:
		id_cuenta: ID de la cuenta (GUID) obtenido de /cuentas/cvus
		skip: Número de registros a saltar (paginación)
		top: Cantidad de registros por página (máximo 100)
		from_date: Fecha de inicio (opcional)
		to_date: Fecha de fin (opcional)
	"""
	try:
		id_usuario = current_user.get("sub")
		if not id_usuario:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="ID de usuario no encontrado en el token"
			)
		
		movimientos = await CuentasService.consultar_movimientos(
			id_cuenta=id_cuenta,
			id_usuario=id_usuario,
			skip=skip,
			top=top,
			from_date=from_date,
			to_date=to_date
		)
		
		return movimientos
		
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error al consultar movimientos: {str(e)}"
		)