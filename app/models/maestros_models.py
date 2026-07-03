
# app\models\maestros.py
from pydantic import BaseModel, Field
from typing import Optional



class Provincia(BaseModel):
	idProvincia: str
	codigoIsoProvincia: str
	nombreProvincia: str
	nombreLocalidad: Optional[str] = None
	idPais: str
	nombrePais: str


class Nacionalidad(BaseModel):
	idWeb: str
	descripcion: str


class EstadoCivil(BaseModel):
	id: str
	descripcion: str


class CondicionFiscal(BaseModel):
	idWeb: str
	descripcion: str


class Ocupacion(BaseModel):
	id: str
	descripcion: str


class MotivoPEP(BaseModel):
	idWeb: str
	descripcion: str


class ErrorMaestro(BaseModel):
    error: str = Field(..., description="Mensaje de error si falló la carga de este dato maestro")


class DatosMaestrosResponse(BaseModel):
	nacionalidades: list[Nacionalidad] | ErrorMaestro
	provincias: list[Provincia] | ErrorMaestro
	estados_civiles: list[EstadoCivil] | ErrorMaestro
	condiciones_fiscales: list[CondicionFiscal] | ErrorMaestro
	ocupaciones: list[Ocupacion] | ErrorMaestro
	motivos_pep: list[MotivoPEP] | ErrorMaestro
