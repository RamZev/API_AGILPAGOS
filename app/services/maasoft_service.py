# app/services/maasoft_service.py
import logging
import httpx
from typing import Optional

from app.config import Config
from app.models.maasoft_models import SocioResponse


logger = logging.getLogger(__name__)


class MaaSoftService:
	"""Servicio para consumir la API de MaaSoft (sistema de socios)"""
	
	#-- URL base de la API de MaaSoft.
	BASE_URL = Config.MAASOFT_BASE_URL
	
	@classmethod
	async def get_socio_cuit(cls, cuit: int) -> Optional[SocioResponse]:
		"""
		Obtiene los datos de un socio por su CUIT.
		
		Args:
			cuit: CUIT del socio (entero)
			
		Returns:
			SocioResponse con los datos del socio
			
		Raises:
			httpx.HTTPStatusError: Si la API responde con error
			Exception: Para otros errores
		"""
		try:
			url = f"{cls.BASE_URL}/socio/{cuit}"
			logger.info(f"Consultando socio con CUIT: {cuit}")
			
			async with httpx.AsyncClient(timeout=30.0) as client:
				response = await client.get(url)
				response.raise_for_status()
				
				data = response.json()
				logger.debug(f"Respuesta de MaaSoft: {data}")
				
				#-- Convertir a modelo Pydantic.
				socio = SocioResponse(**data)
				return socio
				
		except httpx.HTTPStatusError as e:
			logger.error(f"Error HTTP al consultar socio {cuit}: {e.response.status_code}")
			logger.error(f"Respuesta: {e.response.text}")
			raise
			
		except Exception as e:
			logger.error(f"Error al consultar socio {cuit}: {e}")
			raise
	
	@classmethod
	async def get_socio_codigo(cls, codigo: int) -> Optional[SocioResponse]:
		"""
		Obtiene los datos de un socio por su CÓDIGO.
		
		Args:
			codigo: Código del socio (entero)
			
		Returns:
			SocioResponse con los datos del socio
			
		Raises:
			httpx.HTTPStatusError: Si la API responde con error
			Exception: Para otros errores
		"""
		try:
			url = f"{cls.BASE_URL}/sociocodigo/{codigo}"
			logger.info(f"Consultando socio con Código: {codigo}")
			
			async with httpx.AsyncClient(timeout=30.0) as client:
				response = await client.get(url)
				response.raise_for_status()
				
				data = response.json()
				logger.debug(f"Respuesta de MaaSoft: {data}")
				
				#-- Convertir a modelo Pydantic.
				socio = SocioResponse(**data)
				return socio
				
		except httpx.HTTPStatusError as e:
			logger.error(f"Error HTTP al consultar socio {codigo}: {e.response.status_code}")
			logger.error(f"Respuesta: {e.response.text}")
			raise
			
		except Exception as e:
			logger.error(f"Error al consultar socio {codigo}: {e}")
			raise
	
	@classmethod
	async def existe_socio(cls, cuit: int) -> bool:
		"""
		Verifica si un socio existe en MaaSoft.
		
		Args:
			cuit: CUIT del socio
			
		Returns:
			True si el socio existe, False en caso contrario
		"""
		try:
			socio = await cls.get_socio_cuit(cuit)
			return socio is not None
		except Exception:
			return False