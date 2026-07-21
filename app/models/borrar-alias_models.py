# app/models/alias_models.py
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timedelta
from typing import Optional
import re

from app.config import Config


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
