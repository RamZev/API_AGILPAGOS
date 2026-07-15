# app/routers/alias_routers.py
from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import Annotated

from app.models.alias_models import AliasChangeRequest
from app.services.alias_service import AliasService
from app.core.exceptions import AgilpagosValidationError
from app.dependencies import get_current_user


router = APIRouter(prefix="/alias", tags=["Alias"])


@router.put("/cambiar")
async def cambiar_alias(
	id_usuario: Annotated[str, Query()],
	request: AliasChangeRequest,
	# current_user: dict = Depends(get_current_user)
):
	"""
	Cambia el alias de una CVU.

	Validaciones (realizadas en el modelo):
	- El alias debe tener entre 6 y 20 caracteres
	- Solo puede contener letras, números, puntos y guiones
	- Deben pasar al menos 24 horas entre cambios (según fecha_ultimo_cambio enviada)
	"""
	try:
		# id_usuario = current_user.get("sub")
		# if not id_usuario:
		# 	raise HTTPException(
		# 		status_code=status.HTTP_400_BAD_REQUEST,
		# 		detail="ID de usuario no encontrado en el token"
		# 	)
		
		#-- El modelo ya validó todo, solo llama al servicio.
		resultado = await AliasService.cambiar_alias(
			cvu=request.cvu,
			nuevo_alias=request.nuevo_alias,
			id_usuario=id_usuario
		)
		
		return {
			"success": True,
			"message": f"Alias cambiado exitosamente a '{request.nuevo_alias}'",
			# "cvu": request.cvu,
			# "nuevo_alias": request.nuevo_alias,
			# "fecha_cambio": datetime.now().isoformat()  # Para que el cliente actualice su BD
		}
	
	except AgilpagosValidationError as e:
		#-- Error de Agilpagos.
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=str(e)
		)
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error al cambiar alias: {str(e)}"
		)