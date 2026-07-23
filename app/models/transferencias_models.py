# app/models/transferencias_models.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any


class TransferenciaRequest(BaseModel):
	"""Solicitud de transferencia"""
	cuitCredito: str = Field(..., description="CUIT del titular de la cuenta destino")
	cbuCredito: str = Field(..., min_length=22, max_length=22, description="CBU/CVU de la cuenta destino")
	nombreCredito: Optional[str] = Field(None, max_length=100, description="Nombre del titular destino")
	idConcepto: str = Field(..., description="GUID del concepto (ver tabla)")
	importe: float = Field(..., gt=0, description="Importe de la transferencia (máximo 2 decimales)")
	descripcion: str = Field(..., max_length=140, description="Descripción de la transferencia")
	cvuDebito: str = Field(..., min_length=22, max_length=22, description="CVU de origen")
	observaciones: Optional[str] = Field(None, max_length=200, description="Observaciones")
	IdTransaccionEntidad: str = Field(..., description="ID único de la transacción en el sistema cliente")
	
	@field_validator('cuitCredito')
	@classmethod
	def validate_cuit(cls, v: str) -> str:
		"""Valida que el CUIT tenga 11 dígitos"""
		if not v.isdigit() or len(v) != 11:
			raise ValueError("El CUIT debe tener 11 dígitos numéricos")
		return v
	
	@field_validator('cbuCredito')
	@classmethod
	def validate_cbu(cls, v: str) -> str:
		"""Valida que el CBU/CVU tenga 22 dígitos"""
		if not v.isdigit() or len(v) != 22:
			raise ValueError("El CBU/CVU debe tener 22 dígitos numéricos")
		return v
	
	@field_validator('idConcepto')
	@classmethod
	def validate_concepto(cls, v: str) -> str:
		"""Valida que el concepto sea uno de los permitidos"""
		CONCEPTOS_VALIDOS = [
			"45D4F58B-46A2-4754-BBFA-FECB8CF88BFC",  # Varios
			"CC441F51-7531-424E-842A-C3A1DBBBF6CE",  # Alquileres
			"06A17DA8-57A5-4104-819A-F46ACE68E25F",  # Expensas
			"FCEA71F5-7395-4CB0-B816-DA493F0605B5",  # Facturas
			"B3300CA6-948C-4AB3-857E-4B88C29BE404",  # Honorarios
		]
		if v.upper() not in [c.upper() for c in CONCEPTOS_VALIDOS]:
			raise ValueError(f"Concepto inválido. Debe ser uno de: {CONCEPTOS_VALIDOS}")
		return v
	
	@field_validator('importe')
	@classmethod
	def validate_importe(cls, v: float) -> float:
		"""Valida que el importe tenga máximo 2 decimales"""
		if round(v, 2) != v:
			raise ValueError("El importe no puede tener más de 2 decimales")
		if v <= 0:
			raise ValueError("El importe debe ser mayor a 0")
		return v
	
	@field_validator('cvuDebito')
	@classmethod
	def validate_cvu(cls, v: str) -> str:
		"""Valida que el CVU tenga 22 dígitos"""
		if not v.isdigit() or len(v) != 22:
			raise ValueError("El CVU debe tener 22 dígitos numéricos")
		return v


class TransferenciaResponse(BaseModel):
	"""Respuesta de una transferencia"""
	id: str
	estadoDebito: Dict[str, Any]
	impuestosDebito: List[Dict[str, Any]]
	totalDebito: float
	idCredito: Optional[str] = None
	estadoCredito: Optional[Dict[str, Any]] = None
	totalCredito: Optional[float] = 0
	idCoelsa: Optional[str] = None
	
	@classmethod
	def from_agilpagos(cls, data: Dict[str, Any]) -> "TransferenciaResponse":
		"""Crea una instancia desde la respuesta de Agilpagos"""
		return cls(**data)


# --- Modelos para Estados ---

class EstadoTransaccion(BaseModel):
	"""Estado de una transacción"""
	codigo: str
	descripcion: str
	errorCoelsa: Optional[str] = None

class ConsultaEstadoResponse(BaseModel):
	"""Respuesta de consulta de estado de transacción"""
	debito: Dict[str, Any]
	credito: Optional[Dict[str, Any]] = None


# --- Constantes ---

class ConceptoTransferencia:
	"""Conceptos de transferencia permitidos"""
	VARIOS = "45D4F58B-46A2-4754-BBFA-FECB8CF88BFC"
	ALQUILERES = "CC441F51-7531-424E-842A-C3A1DBBBF6CE"
	EXPENSAS = "06A17DA8-57A5-4104-819A-F46ACE68E25F"
	FACTURAS = "FCEA71F5-7395-4CB0-B816-DA493F0605B5"
	HONORARIOS = "B3300CA6-948C-4AB3-857E-4B88C29BE404"
	
	@classmethod
	def get_all(cls) -> List[Dict[str, str]]:
		"""Retorna todos los conceptos con su descripción"""
		return [
			{"id": cls.VARIOS, "descripcion": "Varios", "codigo": "VAR"},
			{"id": cls.ALQUILERES, "descripcion": "Alquileres", "codigo": "ALQ"},
			{"id": cls.EXPENSAS, "descripcion": "Expensas", "codigo": "EXP"},
			{"id": cls.FACTURAS, "descripcion": "Facturas", "codigo": "FAC"},
			{"id": cls.HONORARIOS, "descripcion": "Honorarios", "codigo": "HON"},
		]


class EstadoTransaccionGUID:
	"""Estados posibles de una transacción (según página 23)"""
	PENDIENTE = "FA4B44CA-685B-4625-8C47-81969A6E2598"
	INFORMADO_AL_BANCO = "E24A00E1-10A4-4E23-8D60-61EB055480AF"
	PENDIENTE_CONFIRMACION = "0FFA0273-BC86-4BFA-9144-7FBF415B06EA"
	INFORMADO_CON_ERROR = "1165CCFC-0E13-427A-86D2-E89782F9B2FF"
	PENDIENTE_INFORMAR_INTEGRADOR = "FC3F6A69-BE98-48B9-9842-4AE2C851E2DD"
	ERROR_INFORMAR_INTEGRADOR = "B1CE7121-7802-42DE-8891-64EF6FEB1223"
	PROCESADO = "5FB79B38-00ED-47B8-B7CE-B760CBEAE9D8"
	
	@classmethod
	def es_estado_final(cls, codigo: str) -> bool:
		"""Indica si el estado es final (no requiere más seguimiento)"""
		FINALES = [cls.PROCESADO, cls.INFORMADO_CON_ERROR]
		return codigo.upper() in [f.upper() for f in FINALES]
	
	@classmethod
	def es_pendiente(cls, codigo: str) -> bool:
		"""Indica si el estado es pendiente (requiere seguimiento)"""
		PENDIENTES = [
			cls.PENDIENTE,
			cls.INFORMADO_AL_BANCO,
			cls.PENDIENTE_CONFIRMACION,
			cls.PENDIENTE_INFORMAR_INTEGRADOR,
			cls.ERROR_INFORMAR_INTEGRADOR
		]
		return codigo.upper() in [p.upper() for p in PENDIENTES]