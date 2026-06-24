# app\models\maasoft_models.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date



class SocioResponse(BaseModel):
	"""Modelo para la respuesta de la API de MaaSoft"""
	Codigo: int
	Nombre: str
	Sucursal: int
	Sexo:  Optional[str] = None
	Domicilio: Optional[str] = None
	Codigo_Postal: Optional[int] = Field(None, alias="Codigo Postal")
	CUIT: int
	Tipo_Documento: Optional[str] = Field(None, alias="Tipo Documento")
	Numero_Documento: Optional[int] = Field(None, alias="Numero Documento")
	Estado_Civil: Optional[str] = Field(None, alias="Estado Civil")
	Condicion_Fiscal: Optional[str] = Field(None, alias="Condicion Fiscal")
	Sujeto_Obligado_UIF: Optional[bool] = Field(None, alias="Sujeto Obligado UIF")
	Residente: Optional[str] = None
	Codigo_Pais_Extranjero: Optional[int] = Field(None, alias="Codigo Pais Extranjero")
	Fecha_Nacimiento: Optional[date] = Field(None, alias="Fecha Nacimiento")
	Fecha_Ingreso: Optional[date] = Field(None, alias="Fecha Ingreso")
	Es_PEP: Optional[str] = Field(None, alias="Es PEP")
	Nacionalidad: Optional[str] = None
	Telefono: Optional[str] = None
	Telefono_2: Optional[str] = Field(None, alias="Telefono 2")
	Movil: Optional[str] = None
	e_Mail: Optional[str] = Field(None, alias="e-Mail")
	Codigo_Actividad: Optional[int] = Field(None, alias="Codigo Actividad")
