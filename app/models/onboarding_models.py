# app\models\onboarding.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date


class UsuarioAltaRequest(BaseModel):
	"""Request para el alta de usuario (lo que recibe tu API Intermedia)"""
	
	nombre: str = Field(..., max_length=40)
	apellido: str = Field(..., max_length=40)
	genero: str = Field(..., pattern="^(M|F|X)$")
	fechaNacimiento: date
	idNacionalidad: str
	idTipoDocumento: str
	numeroDocumento: str
	numeroTramiteDocumento: str
	cuit: str = Field(..., pattern="^[0-9]{11}$")
	idEstadoCivil: str
	email: str
	caracteristicaPaisTelefono: str
	codigoAreaTelefono: str
	numeroTelefono: str
	idCondicionFiscal: str
	esPep: bool = False
	idMotivoPep: Optional[str] = None
	esUIF: bool = False
	leyFATCA: bool = False
	idPaisNacimiento: str
	idPaisDomicilio: str
	idProvincia: str
	localidad: str
	calle: str
	altura: str
	cp: str
	piso: Optional[str] = None
	departamento: Optional[str] = None
	observaciones: Optional[str] = None
	fechaAlta: date
	idOcupacion: str
	numeroCuentaEntidad: str
	idEntidadTipoDocumento: str
	idTipoPersona:str
	idTipoCuenta:str
	
	@field_validator('fechaNacimiento')
	def validate_age(cls, v):
		"""Valida que la edad esté entre 13 y 100 años"""
		today = date.today()
		age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
		if age < 13 or age > 100:
			raise ValueError(f"La edad ({age}) debe estar entre 13 y 100 años")
		return v

	@field_validator('email')
	def validate_email(cls, v):
		"""Valida formato de email"""
		import re
		pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
		if not re.match(pattern, v):
			raise ValueError("Formato de email inválido")
		return v


class UsuarioAltaResponse(BaseModel):
	"""Respuesta del alta de usuario (lo que devuelve API Intermedia)"""
	id_usuario: str
	cvu: str
	alias: str
	id_usuario_entidad_lineas_cuentas: str
	numero_cuenta_entidad: str


class UsuarioConsultaResponse(BaseModel):
	"""Respuesta de consulta de usuario por CUIT"""
	id_usuario: str
	cuit: str
	nombre: str
	apellido: str
	email: str
	cvus: list


class ErrorResponse(BaseModel):
	"""Respuesta de error estandarizada"""
	error: bool = True
	message: str
	details: Optional[str] = None
	status_code: int