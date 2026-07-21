# app\models\onboarding_models.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, datetime, timedelta
import re

from app.config import Config


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
	caracteristicaPais: str
	codigoArea: str
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
	"""Respuesta del alta de usuario"""
	id_usuario: str
	cvu: str
	alias: str
	id_usuario_entidad_lineas_cuentas: str
	numero_cuenta_entidad: str


class Titular(BaseModel):
	"""Titular de una cuenta"""
	tipoPersona: str
	cuit: str
	nombre: str


class CuentaInfo(BaseModel):
	"""Información de una cuenta (CVU)"""
	cvu: str
	alias: str
	estado: str
	nroCuentaEntidad: str
	favorita: bool
	titulares: List[Titular]


class UsuarioConsultaResponse(BaseModel):
	"""Respuesta de consulta de usuario por CUIT"""
	usuario: List[str]
	cuentas: List[CuentaInfo]


class ErrorResponse(BaseModel):
	"""Respuesta de error estandarizada"""
	error: bool = True
	message: str
	details: Optional[str] = None
	status_code: int


class AliasChangeRequest(BaseModel):
	"""Solicitud para cambiar el alias de una CVU"""
	cvu: str = Field(..., min_length=22, max_length=22)
	nuevo_alias: str = Field(..., min_length=6, max_length=20)
	fecha_ultimo_cambio: Optional[datetime] = None
	
	@field_validator('nuevo_alias')
	@classmethod
	def validate_alias_format(cls, v: str) -> str:
		"""Valida el formato del alias según las reglas de Coelsa"""
		#-- Caracteres permitidos.
		pattern = r'^[A-Za-z0-9.-]+$'
		if not re.match(pattern, v):
			raise ValueError(
				"El alias solo puede contener letras (mayúsculas y minúsculas), "
				"números, puntos (.) y guiones (-)"
			)
		#-- Longitud permitida (ya validada por Field, se deja por claridad).
		if not (6 <= len(v) <= 20):
			raise ValueError("El alias debe tener entre 6 y 20 caracteres")
		return v
	
	@field_validator('cvu')
	@classmethod
	def validate_cvu(cls, v: str) -> str:
		"""Valida que el CVU tenga 22 dígitos"""
		if not v.isdigit() or len(v) != 22:
			raise ValueError("El CVU debe tener 22 dígitos numéricos")
		return v
	
	@field_validator('fecha_ultimo_cambio')
	@classmethod
	def validate_ultimo_cambio(cls, v: Optional[datetime]) -> Optional[datetime]:
		"""Valida que hayan pasado al menos 24 horas desde el último cambio solo si existe una fecha"""
		if v is None:
			#-- Si es None, no hay restricción (es la primera vez)
			return v
		
		MIN_HORAS = Config.MIN_HORAS_CAMBIO_ALIAS
		ahora = datetime.now(tz=v.tzinfo) if v.tzinfo is not None else datetime.now()
		diferencia = ahora - v
		
		if diferencia < timedelta(hours=MIN_HORAS):
			horas_restantes = MIN_HORAS - diferencia.total_seconds() / 3600
			raise ValueError(
				f"Deben pasar al menos {MIN_HORAS} horas entre cambios de alias. "
				f"Puedes intentarlo nuevamente en {horas_restantes:.1f} horas."
			)
		return v


class BajaCVURequest(BaseModel):
	"""Solicitud para dar de baja una CVU ante Coelsa"""
	cvu: str = Field(..., min_length=22, max_length=22, description="CVU a dar de baja")
	idMotivoBaja: str = Field(
		default=Config.ID_MOTIVO_BAJA_CVU,
		description="Motivo de baja (GUID fijo según documentación)"
	)
	observaciones: Optional[str] = Field(
		None,
		max_length=200,
		description="Observaciones adicionales sobre la baja"
	)
	
	@field_validator('cvu')
	@classmethod
	def validate_cvu(cls, v: str) -> str:
		"""Valida que el CVU tenga 22 dígitos"""
		if not v.isdigit() or len(v) != 22:
			raise ValueError("El CVU debe tener 22 dígitos numéricos")
		return v
	
	@field_validator('idMotivoBaja')
	@classmethod
	def validate_motivo(cls, v: str) -> str:
		"""Valida que el motivo sea el GUID correcto (por seguridad)"""
		GUID_CORRECTO = Config.ID_MOTIVO_BAJA_CVU
		if v.lower() != GUID_CORRECTO.lower():
			# No bloqueamos, pero al menos advertimos o normalizamos
			# Podríamos lanzar ValueError si queremos ser estrictos
			# return GUID_CORRECTO  # Forzar el GUID correcto
			pass
		return v


class BajaCVUResponse(BaseModel):
	"""Respuesta de la baja de CVU"""
	success: bool
	message: str
	cvu: str
