
# app\models\maestros.py
from pydantic import BaseModel
from typing import List, Optional


class Provincia(BaseModel):
	idProvincia: str
	codigoIsoProvincia: str
	nombreProvincia: str
	nombreLocalidad: Optional[str] = None
	idPais: str
	nombrePais: str


class Nacionalidad(BaseModel):
	idWeb: str
	description: str


class EstadoCivil(BaseModel):
	id: str
	description: str


class CondicionFiscal(BaseModel):
	idWeb: str
	descripcion: str


class Ocupacion(BaseModel):
	id: str
	descripcion: str


class MotivoPEP(BaseModel):
	idWeb: str
	descripcion: str


class DatosMaestrosResponse(BaseModel):
	nacionalidades: List[Nacionalidad]
	provincias: List[Provincia]
	estados_civiles: List[EstadoCivil]
	condiciones_fiscales: List[CondicionFiscal]
	ocupaciones: List[Ocupacion]
	motivos_pep: List[MotivoPEP]
