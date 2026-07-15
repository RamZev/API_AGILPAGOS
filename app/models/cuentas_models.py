# app/models/cuentas.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CVUInfo(BaseModel):
	"""Información de una CVU"""
	id: str
	cvu: str
	alias: str
	nroCuentaEntidad: str
	favorita: bool


class SaldoResponse(BaseModel):
	"""Respuesta de consulta de saldo"""
	fecha: datetime
	importe: float
	moneda: str
	linea: str
	idCuenta: str


class MovimientoParams(BaseModel):
	"""Parámetros para consultar movimientos"""
	id_usuario: str
	skip: int = Field(0, ge=0)
	top: int = Field(10, ge=1, le=100)
	from_date: Optional[datetime] = None
	to_date: Optional[datetime] = None


class MovimientoResponse(BaseModel):
	"""Respuesta de consulta de movimientos"""
	id: int
	idWeb: str
	fechaOperacion: datetime
	tipoTransaccion: str
	moneda: str
	importe: float
	descripcion: str
	estado: str
	idWebEstado: str
	idCoelsa: Optional[str] = None
	acreditaSaldoCuenta: bool


class MovimientosResponse(BaseModel):
	"""Respuesta paginada de movimientos"""
	items: List[MovimientoResponse]
	total: int
	page: int
	size: int
	pages: int