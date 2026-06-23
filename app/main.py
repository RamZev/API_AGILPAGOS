# app\main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import Config
from app.routers import auth, maestros, onboarding
from app.core.http_client import agilpagos_client
from app.core import security


#-- Configurar logging.
logging.basicConfig(
	level=getattr(logging, Config.LOG_LEVEL),
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
	"""
	Maneja el ciclo de vida de la aplicación.
	Se ejecuta al iniciar y al cerrar la API.
	"""
	#-- Inicio: Verificar conexión con Agilpagos.
	logger.info("🚀 Iniciando API Gateway - Agilpagos")
	logger.info(f"📡 Entorno: {Config.ENVIRONMENT}")
	logger.info(f"🔗 Agilpagos URL: {Config.AGILPAGOS_BASE_URL}")
	
	# #-- Intentar obtener token de Agilpagos para verificar conexión.
	# try:
	# 	agilpagos_client._get_token()
	# 	logger.info("✅ Conexión con Agilpagos establecida")
	# except Exception as e:
	# 	logger.warning(f"⚠️ No se pudo conectar con Agilpagos: {e}")
	
	yield
	
	#-- Cierre.
	logger.info("👋 Cerrando API Gateway - Agilpagos")


#-- Crear aplicación.
app = FastAPI(
	title="API Gateway - Agilpagos",
	description="API Gateway para consumir los servicios de la API Agilpagos",
	version="1.0.0",
	lifespan=lifespan,
	docs_url="/docs" if not Config.is_production() else None,
	redoc_url="/redoc" if not Config.is_production() else None,
)

#-- Configurar CORS.
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"] if Config.is_development() else [
		#-- En producción, agregar dominios específicos.
		"https://tudominio.com"
	],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

#-- Incluir routers.
app.include_router(auth.router)
app.include_router(maestros.router)
app.include_router(onboarding.router)


@app.get("/")
async def root():
	return {
		"message": "API Gateway - Agilpagos",
		"version": "1.0.0",
		"environment": Config.ENVIRONMENT,
		"status": "operational",
		"docs": "/docs" if not Config.is_production() else None
	}

@app.get("/health")
async def health_check():
	"""Endpoint de verificación de salud"""
	health_status = {
		"status": "healthy",
		"environment": Config.ENVIRONMENT,
		"agilpagos_url": Config.AGILPAGOS_BASE_URL,
		"agilpagos_connected": False
	}
	
	#-- Verificar conexión con Agilpagos.
	try:
		print("intenta tomar el token")
		agilpagos_client._get_token()
		health_status["agilpagos_connected"] = True
		print("El token", agilpagos_client._token)
	except Exception:
		health_status["agilpagos_connected"] = False
		if Config.is_production():
			health_status["status"] = "degraded"
	
	return health_status

@app.post("/get-credentials")
async def get_credentials(username: str, password: str):
	""" Endpoint para obtener las credenciales requeridas para la solicitud del token Bearer en Agilpagos."""
	creds = security.generate_credentials(username=username, password=password)
	return creds

@app.post("/get-token")
async def get_token()


def main():
	"""Punto de entrada para ejecutar con el comando 'api-agilpagos'"""
	import uvicorn
	uvicorn.run(
		"app.main:app",
		host=Config.API_HOST,
		port=Config.API_PORT,
		reload=Config.is_development()
	)

if __name__ == "__main__":
	main()