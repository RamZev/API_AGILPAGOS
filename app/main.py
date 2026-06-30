# app\main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import Config
from app.routers import (
	auth_routers,
	maestros_router,
	onboarding_routers,
	test_routers,
	maasoft_routers,
	cuentas
)


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
app.include_router(auth_routers.router)
app.include_router(maestros_router.router)
app.include_router(onboarding_routers.router)
app.include_router(test_routers.router)
app.include_router(cuentas.router)

if not Config.is_production():
	app.include_router(maasoft_routers.router)

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