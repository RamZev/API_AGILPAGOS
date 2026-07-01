# app/services/onboarding_service.py
"""Servicio para manejar el alta de usuarios y CVU"""

import logging
from typing import Dict, Any, Optional
import httpx

from app.config import Config
from app.core.http_client import agilpagos_client
from app.models.onboarding_models import UsuarioAltaRequest
from app.core.exceptions import (
	AgilpagosValidationError,
	UsuarioYaExisteError
)


logger = logging.getLogger(__name__)


class OnboardingService:
	"""Servicio para manejar el alta de usuarios y CVU"""
	
	#-- Valores constantes (según documentación).
	# ID_TIPO_DOCUMENTO = "209C1CAA-C56D-4E03-BB40-E9EF2F319A3F"
	# ID_PAIS_ARGENTINA = "76B19E61-B8DC-40F4-BFAB-422CBFFE5002"
	# ID_TIPO_PERSONA = "20EB917-7CA8-49E0-9E0B-CA8293218ACA"
	# ID_TIPO_CUENTA = "D2483A34-78BE-40A2-B8CB-07AD4BCF6F61"
	ID_TIPO_DOCUMENTO = Config.API_SG_ID_TIPO_DOCUMENTO
	ID_PAIS_ARGENTINA = Config.API_SG_ID_PAIS_DOMICILIO
	ID_TIPO_PERSONA = Config.API_SG_ID_TIPO_PERSONA
	ID_TIPO_CUENTA = Config.API_SG_ID_TIPO_CUENTA
	
	@classmethod
	async def verificar_usuario_existe(cls, cuit: str) -> Optional[Dict[str, Any]]:
		"""
		Verifica si un usuario ya existe en Agilpagos por su CUIT.
		
		Args:
			cuit: CUIT del usuario
			
		Returns:
			Datos del usuario si existe
		"""
		try:
			response = await agilpagos_client.request(
				method="GET",
				endpoint=f"/Usuarios/{cuit}/UsuarioByCuit"
			)
			logger.info(f"El contenido del response: {response}")
			return response
			
		except httpx.HTTPStatusError as e:
			#-- Capturar específicamente errores HTTP.
			status_code = e.response.status_code
			logger.warning(f"Error HTTP al consultar usuario {cuit}: {status_code}")
			
			if status_code == 404:
				#-- El usuario no existe, no es un error.
				logger.info(f"Usuario con CUIT {cuit} no encontrado (404 esperado)")
				return None
			
			#-- Otros errores HTTP (400, 500, etc.) se propagan.
			logger.error(f"Error HTTP inesperado al consultar usuario {cuit}: {e}")
			raise
		
		except Exception as e:
			#-- Cualquier otro error inesperado.
			logger.error(f"Error inesperado al verificar usuario {cuit}: {e}")
			raise
	
	@classmethod
	async def crear_usuario(cls, request: UsuarioAltaRequest) -> Dict[str, Any]:
		"""
		Crea un usuario y su CVU en Agilpagos.
		
		Args:
			request: Datos del usuario
			
		Returns:
			Respuesta de Agilpagos con los datos del usuario creado
        
		Raises:
            UsuarioYaExisteError: Si el usuario ya tiene CVU creada
            AgilpagosValidationError: Si Agilpagos devuelve un error de validación
		"""
		#-- 1. Verificar si el usuario ya existe.
		logger.info(f"*-- Verificar si existe usuario con cuit: {request.cuit}")
		usuario_existente = await cls.verificar_usuario_existe(request.cuit)
		
		if usuario_existente:
			logger.info(f"*-- Existe un usuario con cuit: {request.cuit}")
			#-- El usuario ya existe, verificar si tiene CVU.
			cvus = usuario_existente.get("cuentas", [])
			if cvus:
				#-- Si ya tiene CVU, no se permite crear otra.
				raise UsuarioYaExisteError(request.cuit, len(cvus))
			
			#-- Si no tiene CVU, solo se necesita crear una nueva CVU.
			logger.info(f"Usuario {request.cuit} existe sin CVU, se creará una nueva")
		else:
			logger.info(f"*-- No existe usuario con cuit: {request.cuit}, se procesde a crear un usuario y cvu.")
		
		#-- 2. Construir el payload para Agilpagos.
		payload = cls._build_payload(request)
		
		#-- 3. Llamar a la API de Agilpagos (crea usuario si no existe, o agrega CVU si existe).
		try:
			response = await agilpagos_client.request(
				method="POST",
				endpoint="/Usuarios",
				json=payload
			)
			
			if "error" in response and response.get("status_code") == 400:
				raise AgilpagosValidationError(response["error"])
			
			return response
			
		except Exception as e:
			logger.error(f"Error al crear usuario: {e}")
			raise
	
	@classmethod
	def _build_payload(cls, request: UsuarioAltaRequest) -> Dict[str, Any]:
		"""Construye el payload para la API de Agilpagos"""
		
		return {
			"nombre": request.nombre,
			"apellido": request.apellido,
			"genero": request.genero,
			"fechaNacimiento": request.fechaNacimiento.isoformat(),
			"idNacionalidad": request.idNacionalidad,
			"idTipoDocumento": cls.ID_TIPO_DOCUMENTO,
			"numeroDocumento": request.numeroDocumento,
			"numeroTramiteDocumento": request.numeroTramiteDocumento,
			"cuit": int(request.cuit),
			"idEstadoCivil": request.idEstadoCivil,
			"email": request.email,
			"caracteristicaPais": request.caracteristicaPais,
			"codigoArea": request.codigoArea,
			"numeroTelefono": request.numeroTelefono,
			"idCondicionFiscal": request.idCondicionFiscal,
			"esPep": request.esPep,
			"idMotivoPep": request.idMotivoPep,
			"esUIF": request.esUIF,
			"leyFATCA": request.leyFATCA,
			"idPaisNacimiento": request.idPaisNacimiento,
			"idPaisDomicilio": cls.ID_PAIS_ARGENTINA,
			"idProvincia": request.idProvincia,
			"localidad": request.localidad,
			"calle": request.calle,
			"altura": request.altura,
			"cp": request.cp,
			"piso": request.piso,
			"departamento": request.departamento,
			"observaciones": request.observaciones,
			"fechaAlta": request.fechaNacimiento.isoformat(),
			"idOcupacion": request.idOcupacion,
			"numeroCuentaEntidad": request.numeroCuentaEntidad,
			"idEntidadTipoDocumento": cls.ID_TIPO_DOCUMENTO,
			"idTipoPersona": cls.ID_TIPO_PERSONA,
			"idTipoCuenta": cls.ID_TIPO_CUENTA
		}