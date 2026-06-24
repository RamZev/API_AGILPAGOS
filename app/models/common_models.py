# app/models/common.py
"""Modelos comunes compartidos entre módulos"""

from pydantic import BaseModel
from typing import Optional, Any

class ErrorResponse(BaseModel):
	"""Respuesta de error estandarizada"""
	error: bool = True
	message: str
	details: Optional[str] = None
	status_code: int

class SuccessResponse(BaseModel):
	"""Respuesta de éxito estandarizada"""
	success: bool = True
	message: str
	data: Optional[Any] = None

class PaginationParams(BaseModel):
	"""Parámetros de paginación"""
	skip: int = 0
	limit: int = 10

class PaginatedResponse(BaseModel):
	"""Respuesta paginada"""
	items: list
	total: int
	page: int
	size: int
	pages: int