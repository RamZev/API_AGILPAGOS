# app\config.py
import os
from dotenv import load_dotenv

#-- Cargar variables de entorno desde .env
load_dotenv()


class Config:
	"""Configuración centralizada de la aplicación"""
	
	#-- Entorno.
	ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
	
	#-- URLs de Agilpagos.
	AMBIENTE_BASE_URL = os.getenv("AMBIENTE_BASE_URL")
	ONBOARDING_BASE_URL = os.getenv("ONBOARDING_BASE_URL")
	INFORMES_BASE_URL = os.getenv("INFORMES_BASE_URL")
	
	#-- Credenciales de Agilpagos.
	API_SG_ID_ENTIDAD = os.getenv("API_SG_ID_ENTIDAD")
	API_SG_APP_ID = os.getenv("API_SG_APP_ID")
	API_SG_API_KEY = os.getenv("API_SG_API_KEY")
	API_SG_USERNAME = os.getenv("API_SG_USERNAME")
	API_SG_PASSWORD = os.getenv("API_SG_PASSWORD")
	
	API_SG_ID_ENTIDAD_TIPO_DOCUMENTO = os.getenv("API_SG_ID_ENTIDAD_TIPO_DOCUMENTO")
	API_SG_CUIT_ENTIDAD = os.getenv("API_SG_CUIT_ENTIDAD")
	API_SG_CBU_ENTIDAD = os.getenv("API_SG_CBU_ENTIDAD")
	
	API_SG_ID_TIPO_PERSONA = os.getenv("API_SG_ID_TIPO_PERSONA")
	API_SG_ID_TIPO_CUENTA = os.getenv("API_SG_ID_TIPO_CUENTA")
	API_SG_ID_TIPO_DOCUMENTO = os.getenv("API_SG_ID_TIPO_DOCUMENTO")
	API_SG_ID_PAIS_DOMICILIO = os.getenv("API_SG_ID_PAIS_DOMICILIO")
	
	#-- URLs de Agilpagos.
	MAASOFT_BASE_URL = os.getenv("MAASOFT_BASE_URL")
	
	#-- Configuración de la API.
	API_PORT = int(os.getenv("API_PORT", 8081))
	API_HOST = os.getenv("API_HOST", "0.0.0.0")
	
	#-- Logs.
	LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
	
	#-- JWT interno.
	JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
	JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
	JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(
		os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30)
	)
	
	#-- Otros parámetros.
	MIN_HORAS_CAMBIO_ALIAS = int(os.getenv("MIN_HORAS_CAMBIO_ALIAS", 24))
	ID_MOTIVO_BAJA_CVU = os.getenv("ID_MOTIVO_BAJA_CVU")
	
	@classmethod
	def validate(cls):
		"""Valida que las credenciales necesarias estén configuradas"""
		required = [
			"AMBIENTE_BASE_URL",
			"ONBOARDING_BASE_URL",
			"INFORMES_BASE_URL",
			"MAASOFT_BASE_URL",
			"API_SG_ID_ENTIDAD",
			"API_SG_APP_ID",
			"API_SG_API_KEY", 
			"API_SG_USERNAME",
			"API_SG_PASSWORD",
			"API_SG_ID_ENTIDAD_TIPO_DOCUMENTO",
			"API_SG_CUIT_ENTIDAD",
			"API_SG_CBU_ENTIDAD",
			"API_SG_ID_TIPO_PERSONA",
			"API_SG_ID_TIPO_CUENTA",
			"JWT_SECRET_KEY",
			"MIN_HORAS_CAMBIO_ALIAS",
		]
		missing = [field for field in required if not getattr(cls, field)]
		if missing:
			raise ValueError(
				f"❌ Faltan variables de entorno: {', '.join(missing)}\n"
				f"Por favor, revisa tu archivo .env"
			)
	
	@classmethod
	def is_development(cls) -> bool:
		return cls.ENVIRONMENT == "development"
	
	@classmethod
	def is_testing(cls) -> bool:
		return cls.ENVIRONMENT == "testing"
	
	@classmethod
	def is_production(cls) -> bool:
		return cls.ENVIRONMENT == "production"

#-- Validar configuración al importar.
Config.validate()