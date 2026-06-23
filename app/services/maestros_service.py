# app\services\maestros_service.py
import logging
from typing import Dict, Any

from app.core.http_client import agilpagos_client


logger = logging.getLogger(__name__)


class MaestrosService:
	"""Servicio para obtener datos maestros (catálogos) de Agilpagos"""
	
	#-- Constante: ID de Argentina (según documentación).
	ID_PAIS_ARGENTINA = "AC98A1E7-CF65-4430-BF16-24439F35853B"
	
	@classmethod
	async def get_nacionalidades(cls) -> list:
		"""Obtiene el listado de nacionalidades"""
		try:
			response = await agilpagos_client.request(
				method="GET",
				endpoint="/OnBoarding/Nacionalidades",
				requires_auth=False
			)
			return response
		except Exception as e:
			logger.error(f"Error al obtener nacionalidades: {e}")
			raise
	
	@classmethod
	async def get_provincias(cls) -> list:
		"""Obtiene el listado de provincias argentinas"""
		try:
			response = await agilpagos_client.request(
				method="GET",
				endpoint=f"/OnBoarding/Provincias/Pais/{cls.ID_PAIS_ARGENTINA}",
				requires_auth=False
			)
			return response
		except Exception as e:
			logger.error(f"Error al obtener provincias: {e}")
			raise
	
	@classmethod
	async def get_estados_civiles(cls) -> list:
		"""Obtiene el listado de estados civiles"""
		try:
			response = await agilpagos_client.request(
				method="GET",
				endpoint="/OnBoarding/EstadoCivil",
				requires_auth=False
			)
			return response
		except Exception as e:
			logger.error(f"Error al obtener estados civiles: {e}")
			raise
	
	@classmethod
	async def get_condiciones_fiscales(cls) -> list:
		"""Obtiene el listado de condiciones fiscales"""
		try:
			response = await agilpagos_client.request(
				method="GET",
				endpoint="/OnBoarding/CondicionesFiscales",
				requires_auth=False
			)
			return response
		except Exception as e:
			logger.error(f"Error al obtener condiciones fiscales: {e}")
			raise
	
	@classmethod
	async def get_ocupaciones(cls) -> list:
		"""Obtiene el listado de ocupaciones"""
		try:
			response = await agilpagos_client.request(
				method="GET",
				endpoint="/OnBoarding/Ocupaciones",
				requires_auth=False
			)
			return response
		except Exception as e:
			logger.error(f"Error al obtener ocupaciones: {e}")
			raise
	
	@classmethod
	async def get_motivos_pep(cls) -> list:
		"""Obtiene el listado de motivos para Personas Expuestas Políticamente"""
		try:
			response = await agilpagos_client.request(
				method="GET",
				endpoint="/OnBoarding/MotivosPEP",
				requires_auth=False
			)
			return response
		except Exception as e:
			logger.error(f"Error al obtener motivos PEP: {e}")
			raise
	
	@classmethod
	async def get_all(cls) -> Dict[str, Any]:
		"""Obtiene todos los datos maestros en una sola llamada"""
		try:
			#-- Ejecutar todas las consultas en paralelo (más eficiente).
			import asyncio
			resultados = await asyncio.gather(
				cls.get_nacionalidades(),
				cls.get_provincias(),
				cls.get_estados_civiles(),
				cls.get_condiciones_fiscales(),
				cls.get_ocupaciones(),
				cls.get_motivos_pep(),
				return_exceptions=True
			)
			
			#-- Procesar resultados.
			nombres = [
				"nacionalidades", "provincias", "estados_civiles",
				"condiciones_fiscales", "ocupaciones", "motivos_pep"
			]
			
			datos = {}
			for nombre, resultado in zip(nombres, resultados):
				if isinstance(resultado, Exception):
					logger.error(f"Error en {nombre}: {resultado}")
					datos[nombre] = {"error": str(resultado)}
				else:
					datos[nombre] = resultado
			
			return datos
			
		except Exception as e:
			logger.error(f"Error al obtener todos los datos maestros: {e}")
			raise