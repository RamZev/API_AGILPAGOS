# app/services/alias_service.py
import logging
from typing import Dict, Any

from app.core.http_client import agilpagos_client
from app.core.exceptions import AgilpagosValidationError


logger = logging.getLogger(__name__)


class AliasService:
	"""Servicio para gestionar alias de CVU"""
	
	@classmethod
	async def cambiar_alias(
		cls,
		cvu: str,
		nuevo_alias: str,
		id_usuario: str
	) -> Dict[str, Any]:
		"""
		Cambia el alias de una CVU.
		
		Args:
			cvu: CVU a modificar
			nuevo_alias: Nuevo alias (ya validado)
			id_usuario: GUID del usuario (para el header)
		
		Returns:
			Respuesta de Agilpagos
		
		Raises:
			AgilpagosValidationError: Si Agilpagos rechaza el cambio
		"""
		headers = {"IDWEBUSUARIOFINAL": id_usuario}
		
		try:
			response = await agilpagos_client.request(
				method="PUT",
				endpoint=f"/Alias/{cvu}",
				json={"newAlias": nuevo_alias},
				headers=headers
			)

			#-- Agilpagos devuelve 200 OK si el cambio fue exitoso.
			return {"success": True, "message": "Alias cambiado exitosamente"}
		
		except Exception as e:
			logger.error(f"Error al cambiar alias: {e}")
			raise AgilpagosValidationError(f"Error al cambiar alias: {str(e)}")