# app/services/onboarding_service.py
"""Servicio para manejar el alta de usuarios y CVU"""

import logging
from typing import Dict, Any, Optional
import httpx

from app.config import Config
from app.core.http_client import agilpagos_client
from app.models.onboarding_models import UsuarioAltaRequest, BajaCVURequest
from app.core.exceptions import (
	AgilpagosValidationError,
	UsuarioYaExisteError
)


logger = logging.getLogger(__name__)


class OnboardingService:
	"""Servicio para manejar el Onboarding de usuarios"""
	
	#-- Valores constantes (según documentación).
	ID_TIPO_DOCUMENTO = Config.API_SG_ID_TIPO_DOCUMENTO
	ID_PAIS_ARGENTINA = Config.API_SG_ID_PAIS_DOMICILIO
	API_SG_ID_ENTIDAD_TIPO_DOCUMENTO = Config.API_SG_ID_ENTIDAD_TIPO_DOCUMENTO
	ID_TIPO_PERSONA = Config.API_SG_ID_TIPO_PERSONA
	ID_TIPO_CUENTA = Config.API_SG_ID_TIPO_CUENTA
	
	@classmethod
	async def verificar_usuario_existe(cls, cuit: str) -> Optional[Dict[str, Any]]:
		"""
		Verifica si un usuario ya existe en Agilpagos por su CUIT.
		
		Args:
		- cuit: CUIT del usuario
			
		Returns:
		- Datos del usuario si existe
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
		- request: Datos del usuario
			
		Returns:
		- Respuesta de Agilpagos con los datos del usuario creado
		
		Raises:
		- UsuarioYaExisteError: Si el usuario ya tiene CVU creada
		- AgilpagosValidationError: Si Agilpagos devuelve un error de validación
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
				service_type="onboarding",
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
			"idEntidadTipoDocumento": cls.API_SG_ID_ENTIDAD_TIPO_DOCUMENTO,
			"idTipoPersona": cls.ID_TIPO_PERSONA,
			"idTipoCuenta": cls.ID_TIPO_CUENTA
		}

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
			print(f"Resultado (Service): {response}")
			#-- Agilpagos devuelve 200 OK si el cambio fue exitoso.
			return {"success": True, "message": "Alias cambiado exitosamente"}
		
		except Exception as e:
			logger.error(f"Error al cambiar alias: {e}")
			raise AgilpagosValidationError(f"Error al cambiar alias: {str(e)}")	
	
	@classmethod
	async def baja_cvu(
		cls,
		request: BajaCVURequest,
		id_usuario: str
	) -> Dict[str, Any]:
		"""
		Da de baja una CVU ante Coelsa (eliminación definitiva).
		
		Args:
			request: Datos de la solicitud (cvu, idMotivoBaja, observaciones)
			id_usuario: GUID del usuario (para el header IDWEBUSUARIOFINAL)
		
		Returns:
			Respuesta de Agilpagos (vacía si es exitoso, o error)
		
		Raises:
			AgilpagosValidationError: Si Agilpagos devuelve un error
			ValueError: Si la CVU no existe o hay otros problemas
		"""
		headers = {"IDWEBUSUARIOFINAL": id_usuario}
		
		#-- Construir el body de la solicitud.
		body = {
			"idMotivoBaja": request.idMotivoBaja
		}
		if request.observaciones:
			body["observaciones"] = request.observaciones
		
		try:
			logger.info(f"🔄 Dando de baja CVU: {request.cvu} para usuario {id_usuario}")
			
			#-- El endpoint de baja es DELETE /CVU/{cvu}.
			response = await agilpagos_client.request(
				method="DELETE",
				endpoint=f"/CVU/{request.cvu}",
				json=body,
				headers=headers
			)
			
			#-- Si Agilpagos devuelve 200 OK, la baja fue exitosa.
			logger.info(f"✅ CVU {request.cvu} dada de baja exitosamente")
			return response or {"message": "Baja exitosa"}
			
		except Exception as e:
			logger.error(f"❌ Error al dar de baja CVU {request.cvu}: {e}")
			
			#-- Intentar extraer el mensaje de error de Agilpagos si está disponible.
			if hasattr(e, 'response'):
				try:
					error_data = e.response.json()
					error_message = error_data.get('errors', {}).get('', ['Error desconocido'])[0]
					raise AgilpagosValidationError(f"Error de Agilpagos: {error_message}")
				except:
					pass
			
			raise AgilpagosValidationError(f"Error al dar de baja la CVU: {str(e)}")
	
	@classmethod
	async def verificar_cvu_pertenece_usuario(
		cls,
		cvu: str,
		id_usuario: str
	) -> bool:
		"""
		Verifica que una CVU pertenezca al usuario.
		
		Args:
			cvu: CVU a verificar
			id_usuario: GUID del usuario
		
		Returns:
			True si la CVU pertenece al usuario, False en caso contrario
		"""
		try:
			#-- Obtener todas las CVU del usuario.
			headers = {"IDWEBUSUARIOFINAL": id_usuario}
			response = await agilpagos_client.request(
				method="GET",
				endpoint="/CVU",
				headers=headers
			)
			
			#-- Verificar si el CVU está en la lista.
			if isinstance(response, list):
				for cuenta in response:
					if cuenta.get("cvu") == cvu:
						return True
			return False
			
		except Exception as e:
			logger.error(f"Error al verificar propiedad de CVU: {e}")
			#-- En caso de error, asumimos que no pertenece (por seguridad).
			return False
