import os
from dotenv import load_dotenv
from typing import Optional

# Cargar variables de entorno desde .env
load_dotenv()

class Config:
	"""Configuración centralizada de la aplicación"""
	
	# Entorno
	ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
	
	# URLs de Agilpagos
	AGILPAGOS_BASE_URL = os.getenv("AGILPAGOS_BASE_URL", "http://localhost:8000")
	
	# Credenciales de Agilpagos
	API_SG_ID_ENTIDAD = os.getenv("API_SG_ID_ENTIDAD")
	API_SG_APP_ID = os.getenv("API_SG_APP_ID")
	API_SG_API_KEY = os.getenv("API_SG_API_KEY")
	API_SG_USERNAME = os.getenv("API_SG_USERNAME")
	API_SG_PASSWORD = os.getenv("API_SG_PASSWORD")
	
	# Configuración de la API
	API_PORT = int(os.getenv("API_PORT", 8080))
	API_HOST = os.getenv("API_HOST", "0.0.0.0")
	
	# Logs
	LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
	
	# JWT interno
	JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
	JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
	JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(
		os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30)
	)
	
	@classmethod
	def validate(cls):
		"""Valida que las credenciales necesarias estén configuradas"""
		required = [
			"API_SG_ID_ENTIDAD", "API_SG_APP_ID", "API_SG_API_KEY", 
			"API_SG_USERNAME", "API_SG_PASSWORD", "JWT_SECRET_KEY"
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

# Validar configuración al importar
Config.validate()