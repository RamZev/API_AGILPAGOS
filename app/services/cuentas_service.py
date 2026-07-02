# app/services/cuentas_service.py
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.http_client import agilpagos_client
from app.models.cuentas_models import CVUInfo, SaldoResponse, MovimientoResponse

logger = logging.getLogger(__name__)


class CuentasService:
	"""Servicio para manejar cuentas (CVU), saldos y movimientos"""
	
	@classmethod
	async def listar_cvus(cls, id_usuario: str) -> List[CVUInfo]:
		"""
		Obtiene la lista de CVU de un usuario.
		
		Args:
			- id_usuario: GUID del usuario en Agilpagos
			
		Returns:
			- Lista de CVUInfo
		"""
		try:
			#-- El endpoint /CVU requiere el header IDWEBUSUARIOFINAL.
			headers = {"IDWEBUSUARIOFINAL": id_usuario}
			
			response = await agilpagos_client.request(
				method="GET",
				endpoint="/CVU",
				headers=headers
			)
			
			#-- La respuesta es una lista de CVU.
			if isinstance(response, list):
				return [CVUInfo(**item) for item in response]
			return []
			
		except Exception as e:
			logger.error(f"Error al listar CVU del usuario {id_usuario}: {e}")
			raise
	
	@classmethod
	async def consultar_saldo(cls, id_cuenta: str) -> SaldoResponse:
		"""
		Consulta el saldo de una CVU.
		
		Args:
			- id_cuenta: ID de la cuenta (GUID obtenido de /CVU)
			
		Returns:
			- SaldoResponse con el saldo y fecha
		"""
		try:
			response = await agilpagos_client.request(
				method="GET",
				endpoint=f"/Saldos/{id_cuenta}"
			)
			
			return SaldoResponse(**response)
			
		except Exception as e:
			logger.error(f"Error al consultar saldo de cuenta {id_cuenta}: {e}")
			raise
	
	@classmethod
	async def consultar_movimientos(
		cls,
		id_cuenta: str,
		id_usuario: str,
		skip: int = 0,
		top: int = 10,
		from_date: Optional[datetime] = None,
		to_date: Optional[datetime] = None
	) -> Dict[str, Any]:
		"""
		Consulta los movimientos de una CVU con paginación.
		
		Args:
			- id_cuenta: ID de la cuenta (GUID)
			- id_usuario: GUID del usuario (para el header)
			- skip: Número de registros a saltar (paginación)
			- top: Cantidad de registros por página
			- from_date: Fecha de inicio (opcional)
			- to_date: Fecha de fin (opcional)
			
		Returns:
			- Diccionario con items, total, page, size, pages
		"""
		try:
			# Construir parámetros de query
			params = {
				"idUsuarioLineaCuenta": id_cuenta,
				"$skip": skip,
				"$top": top
			}
			
			if from_date:
				params["$from"] = from_date.isoformat()
			if to_date:
				params["$to"] = to_date.isoformat()
			
			# Header obligatorio
			headers = {"IDWEBUSUARIOFINAL": id_usuario}
			
			response = await agilpagos_client.request(
				method="GET",
				endpoint="/Transacciones",
				params=params,
				headers=headers
			)
			
			# La respuesta es una lista de movimientos
			if isinstance(response, list):
				items = [MovimientoResponse(**item) for item in response]
			else:
				items = []
			
			# Obtener información de paginación desde el header (si está disponible)
			# Nota: La paginación se maneja con los parámetros skip y top
			return {
				"items": items,
				"total": len(items),  # En producción, esto vendría del header X-Pagination
				"page": (skip // top) + 1 if top > 0 else 1,
				"size": top,
				"pages": 1  # Se calcula a partir del total
			}
			
		except Exception as e:
			logger.error(f"Error al consultar movimientos de cuenta {id_cuenta}: {e}")
			raise