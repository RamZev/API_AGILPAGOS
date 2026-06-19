# app\core\http_client.py
import httpx
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio

from app.config import Config
from app.core.security import generate_credentials

logger = logging.getLogger(__name__)

class AgilpagosClient:
	"""
	Cliente HTTP para consumir la API de Agilpagos.
	Maneja la autenticación, renovación de token y reintentos.
	"""
	
	def __init__(self):
		self.base_url = Config.AGILPAGOS_BASE_URL
		self.id_entidad = Config.ID_ENTIDAD
		self.username = Config.USERNAME
		self.password = Config.PASSWORD
		
		self._token: Optional[str] = None
		self._token_expiration: Optional[datetime] = None
		
		# Cliente HTTP con timeout configurable
		self._client = httpx.Client(
			timeout=30.0,
			limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
		)
		
		logger.info(f"Cliente Agilpagos inicializado con URL: {self.base_url}")
	
	def _get_token(self) -> str:
		"""Obtiene un token Bearer válido, renovándolo si es necesario"""
		if not self._token or self._is_token_expired():
			self._refresh_token()
		print(f"Token recibido de Agilpagos: {self._token}")
		return self._token
	
	def _is_token_expired(self) -> bool:
		"""Verifica si el token está por expirar (menos de 5 minutos de margen)"""
		if not self._token_expiration:
			return True
		margin = timedelta(minutes=5)
		return datetime.now() >= (self._token_expiration - margin)
	
	def _refresh_token(self):
		"""Renueva el token llamando al endpoint /Account/Login"""
		logger.info("🔄 Renovando token de autenticación...")
		
		# Generar credenciales
		creds = generate_credentials(self.username, self.password)
		
		# Preparar payload
		payload = {
			"idEntidad": self.id_entidad,
			"userName": creds["username"],
			"password": creds["password"],
			"nonce": creds["nonce"],
			"created": creds["created"]
		}
		
		try:
			response = self._client.post(
				f"{self.base_url}/Account/Login",
				json=payload
			)
			response.raise_for_status()
			
			data = response.json()
			self._token = data.get("token")
			
			# Parsear fecha de expiración
			exp_str = data.get("expiration")
			if exp_str:
				# Manejar formato ISO con Z
				self._token_expiration = datetime.fromisoformat(
					exp_str.replace("Z", "+00:00")
				)
			
			logger.info("✅ Token renovado exitosamente")
			
			if self._token_expiration:
				logger.info(f"⏰ Expiración: {self._token_expiration}")
			
		except httpx.HTTPStatusError as e:
			logger.error(f"❌ Error HTTP al renovar token: {e.response.status_code}")
			logger.error(f"   Respuesta: {e.response.text}")
			raise
		except Exception as e:
			logger.error(f"❌ Error al renovar token: {e}")
			raise
	
	def request(
		self,
		method: str,
		endpoint: str,
		json: Optional[Dict[str, Any]] = None,
		params: Optional[Dict[str, Any]] = None,
		headers: Optional[Dict[str, str]] = None,
		retries: int = 3
	) -> Dict[str, Any]:
		"""
		Realiza una solicitud HTTP a la API de Agilpagos.
		
		Args:
			method: Método HTTP (GET, POST, PUT, DELETE)
			endpoint: Endpoint relativo (ej: "/Usuarios")
			json: Body de la solicitud
			params: Parámetros de query string
			headers: Headers adicionales
			retries: Número de reintentos en caso de error
			
		Returns:
			Respuesta JSON de Agilpagos
		"""
		url = f"{self.base_url}{endpoint}"
		token = self._get_token()
		
		# Headers base
		request_headers = {
			"Authorization": f"Bearer {token}",
			"Content-Type": "application/json",
			"Accept": "application/json"
		}
		
		if headers:
			request_headers.update(headers)
		
		for attempt in range(retries):
			try:
				logger.debug(f"📤 Request {method} {url}")
				if json:
					logger.debug(f"   Body: {json}")
				
				response = self._client.request(
					method=method,
					url=url,
					json=json,
					params=params,
					headers=request_headers
				)
				
				# Si el token expiró, renovar y reintentar
				if response.status_code == 401:
					logger.warning("🔑 Token expirado, renovando...")
					self._refresh_token()
					request_headers["Authorization"] = f"Bearer {self._token}"
					continue
				
				# Si es error 400, no reintentar (error lógico)
				if response.status_code == 400:
					logger.warning(f"⚠️ Error lógico en solicitud: {response.text}")
					return {"error": response.text, "status_code": 400}
				
				response.raise_for_status()
				
				if response.status_code == 204:
					return {}
				
				return response.json()
				
			except httpx.HTTPStatusError as e:
				if attempt == retries - 1:
					logger.error(f"❌ Error después de {retries} intentos: {e}")
					raise
				
				# Reintentar solo en errores de servidor (5xx)
				if 500 <= e.response.status_code < 600:
					wait_time = 2 ** attempt  # Backoff exponencial
					logger.warning(f"⏳ Reintento {attempt + 1}/{retries} en {wait_time}s")
					time.sleep(wait_time)
					continue
				else:
					# Errores 4xx no se reintentan
					raise
				
			except (httpx.ConnectError, httpx.TimeoutException) as e:
				if attempt == retries - 1:
					logger.error(f"❌ Error de conexión después de {retries} intentos: {e}")
					raise
				
				wait_time = 2 ** attempt
				logger.warning(f"⏳ Reintento {attempt + 1}/{retries} en {wait_time}s")
				time.sleep(wait_time)
				continue
				
			except Exception as e:
				if attempt == retries - 1:
					logger.error(f"❌ Error inesperado: {e}")
					raise
				continue
		
		return {}

# Singleton para reutilizar en toda la aplicación
agilpagos_client = AgilpagosClient()

# Importar time para el backoff
import time