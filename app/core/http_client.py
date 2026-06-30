# app/core/http_client.py
import httpx
import logging
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from app.config import Config
from app.core.security import generate_credentials


logger = logging.getLogger(__name__)


class AgilpagosClient:
	"""Cliente HTTP para consumir la API de Agilpagos."""
	
	def __init__(self):
		self.base_url = Config.AGILPAGOS_BASE_URL
		self.id_entidad = Config.API_SG_ID_ENTIDAD
		self.username = Config.API_SG_USERNAME
		self.password = Config.API_SG_PASSWORD
		self.cuit_entidad = Config.API_SG_CUIT_ENTIDAD
		
		self._token: Optional[str] = None
		self._token_expiration: Optional[datetime] = None
		self._refresh_token_value: Optional[str] = None
		
		self._client = httpx.AsyncClient(
			timeout=30.0,
			limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
		)
		
		logger.info(f"Cliente Agilpagos inicializado con URL: {self.base_url}")
	
	async def _get_token(self) -> str|None:
		"""Obtiene un token Bearer válido, renovándolo si es necesario"""
		if not self._token or self._is_token_expired():
			await self._refresh_token()
		return self._token
	
	def _is_token_expired(self) -> bool:
		"""Verifica si el token está por expirar (menos de 5 minutos de margen)"""
		print("*-- viene a comprobar le expiración del token")
		if not self._token_expiration:
			return True
		margin = timedelta(minutes=5)
		print(f"*-- margin: {margin}")
		print(f"*-- type(margin): {type(margin)}")
		dif = datetime.now() >= (self._token_expiration - margin)
		print(f"*-- dif: {dif}")
		return datetime.now() >= (self._token_expiration - margin)
	
	async def _refresh_token(self):
		"""Renueva el token usando refreshToken si está disponible, o login completo"""
		if self._refresh_token_value:
			try:
				await self._refresh_with_refresh_token()
				return
			except Exception as e:
				logger.warning(f"⚠️ Falló renovación con refreshToken: {e}")
				logger.info("🔄 Intentando login completo como fallback...")
		
		await self._refresh_with_login()
	
	async def _refresh_with_refresh_token(self):
		"""Renueva el token usando el endpoint /Account/RefreshToken"""
		logger.info("🔄 Renovando token con refreshToken...")
		
		payload = {"refreshToken": self._refresh_token_value}
		
		try:
			response = await self._client.post(
				f"{self.base_url}/Account/RefreshToken",
				json=payload
			)
			response.raise_for_status()
			
			data = response.json()
			self._token = data.get("token")
			
			new_refresh = data.get("refreshToken")
			if new_refresh:
				self._refresh_token_value = new_refresh
			
			exp_str = data.get("expiration")
			if exp_str:
				self._token_expiration = datetime.fromisoformat(
					exp_str.replace("Z", "+00:00")
				)
			
			logger.info("✅ Token renovado exitosamente con refreshToken")
			
		except Exception as e:
			logger.error(f"❌ Error al renovar con refreshToken: {e}")
			raise
	
	async def _refresh_with_login(self):
		"""Renueva el token haciendo login completo (fallback)"""
		logger.info("🔄 Renovando token con login completo...")
		
		if self.username is None or self.password is None:
			raise ValueError("Missing API_SG_USERNAME or API_SG_PASSWORD")
		
		creds = generate_credentials(self.username, self.password)
		
		payload = {
			"idEntidad": creds["idEntidad"],
			"userName": creds["userName"],
			"password": creds["password"],
			"nonce": creds["nonce"],
			"created": creds["created"],
			"cuit": creds["cuit"]
		}
		logger.info(f"payload: {payload}")
		try:
			response = await self._client.post(
				f"{self.base_url}/Account/Login",
				json=payload
			)
			response.raise_for_status()
			
			data = response.json()
			self._token = data.get("token")
			self._refresh_token_value = data.get("refreshToken")
			self._token_expiration = data.get("expiration")
			
			exp_str = data.get("expiration")
			if exp_str:
				self._token_expiration = datetime.fromisoformat(
					exp_str.replace("Z", "+00:00")
				)
			
			logger.info("✅ Token renovado exitosamente con login")
			
		except Exception as e:
			logger.error(f"❌ Error al renovar token con login: {e}")
			raise
	
	async def request(
		self,
		method: str,
		endpoint: str,
		json: Optional[Dict[str, Any]] = None,
		params: Optional[Dict[str, Any]] = None,
		headers: Optional[Dict[str, str]] = None,
		retries: int = 3,
		requires_auth: bool = True
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
			requires_auth: Si es True, incluye el token Bearer. 
						   Para endpoints públicos, usa False.
		"""
		url = f"{self.base_url}{endpoint}"
		
		#-- Headers base (sin token por defecto).
		request_headers = {
			"Content-Type": "application/json",
			"Accept": "application/json"
		}
		
		#-- Solo agregar Authorization si se requiere.
		if requires_auth:
			token = await self._get_token()
			request_headers["Authorization"] = f"Bearer {token}"
		
		if headers:
			request_headers.update(headers)
		
		for attempt in range(retries):
			try:
				logger.debug(f"📤 Request {method} {url}")
				if json:
					logger.debug(f"   Body: {json}")
				
				response = await self._client.request(
					method=method,
					url=url,
					json=json,
					params=params,
					headers=request_headers
				)
				
				#-- Si el token expiró, renovar y reintentar (solo si requiere auth).
				if requires_auth and response.status_code == 401:
					logger.warning("🔑 Token expirado, renovando...")
					await self._refresh_token()
					request_headers["Authorization"] = f"Bearer {self._token}"
					continue
				
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
				
				if 500 <= e.response.status_code < 600:
					wait_time = 2 ** attempt
					logger.warning(f"⏳ Reintento {attempt + 1}/{retries} en {wait_time}s")
					import asyncio
					await asyncio.sleep(wait_time)
					continue
				else:
					raise
				
			except (httpx.ConnectError, httpx.TimeoutException) as e:
				if attempt == retries - 1:
					logger.error(f"❌ Error de conexión después de {retries} intentos: {e}")
					raise
				
				wait_time = 2 ** attempt
				logger.warning(f"⏳ Reintento {attempt + 1}/{retries} en {wait_time}s")
				import asyncio
				await asyncio.sleep(wait_time)
				continue
				
			except Exception as e:
				if attempt == retries - 1:
					logger.error(f"❌ Error inesperado: {e}")
					raise
				continue
		
		return {}


#-- Singleton.
agilpagos_client = AgilpagosClient()