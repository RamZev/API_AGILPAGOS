# app/core/security.py
import hashlib
import base64
import uuid
from datetime import datetime, timezone
import jwt
from typing import Optional
from datetime import timedelta

from app.config import Config

''' generate_credentials (Original) ---------------------------
def generate_credentials(username: str, password: str) -> dict:
	"""
	Genera las credenciales para el login de Agilpagos.
	Implementa el algoritmo SHA1 + nonce + timestamp.
	
	Args:
		username: Nombre de usuario
		password: Contraseña en texto plano
	
	Returns:
		Diccionario con username, password (hasheada), nonce y created
	"""
	# 1. Generar fecha UTC en formato YYYY-MM-DDTHH:MM:SSZ
	created = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S") + "Z"
	
	# 2. Generar nonce aleatorio (GUID sin guiones)
	nonce = uuid.uuid4().hex
	
	# 3. Convertir a bytes y concatenar: nonce + created + password
	nonce_bytes = nonce.encode('utf-8')
	created_bytes = created.encode('utf-8')
	password_bytes = password.encode('utf-8')
	
	concatenated = nonce_bytes + created_bytes + password_bytes
	
	# 4. Calcular hash SHA1
	sha1_hash = hashlib.sha1(concatenated).digest()
	
	# 5. Codificar en Base64
	hashed_password = base64.b64encode(sha1_hash).decode('utf-8')
	return {
		"username": username,
		"password": hashed_password,
		"nonce": nonce,
		"created": created
	}
'''

def generate_credentials(username: str, password: str) -> dict:
	"""
	Genera las credenciales para el login de Agilpagos.
	Implementa el algoritmo SHA1 + nonce + timestamp.
	
	Usa un nonce de 16 bytes en Base64 y excluye la 'Z' en el cálculo del hash SHA1.
	
	Args:
		username: Nombre de usuario
		password: Contraseña en texto plano
	
	Returns:
		Diccionario con username, password (hasheada), nonce y created
	"""
	#-- Generar la fecha UTC en formato ISO sin 'Z' (se agregará al final).
	fecha_base = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
	created = fecha_base + "Z"
	
	#-- Generar un nonce real de 16 bytes binarios (UUID4) y codificarlo en Base64 string.
	nonce_bytes_original = uuid.uuid4().bytes  #-- 16 bytes puros.
	nonce_b64_str = base64.b64encode(nonce_bytes_original).decode("utf-8")
	
	#-- Preparar los inputs para el Hash.
	#-- Se obtienen los 16 bytes binarios a partir del Base64 string.
	nonce_hash_bytes = base64.b64decode(nonce_b64_str)
	# La fecha se procesa en bytes SIN la 'Z'
	created_hash_bytes = fecha_base.encode("utf-8")
	password_bytes = password.encode("utf-8")
	
	#-- Concatenar: nonce (16 bytes) + fecha (sin Z) + password.
	concatenated = nonce_hash_bytes + created_hash_bytes + password_bytes
	
	#-- Calcular el hash SHA1 y codificar el resultado en Base64.
	sha1_hash = hashlib.sha1(concatenated).digest()
	hashed_password = base64.b64encode(sha1_hash).decode("utf-8")
	
	print(f"username: {username}")
	print(f"password: {hashed_password}")
	print(f"nonce: {nonce_b64_str}")
	print(f"created: {created}")
	
	return {
		"userName": username,
		"password": hashed_password,
		"nonce": nonce_b64_str,
		"created": created,
		"idEntidad": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
		"cuit": 0
	}


def create_jwt_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
	"""
	Crea un token JWT interno para usuarios de la API Intermedia.
	"""
	to_encode = data.copy()
	
	if expires_delta:
		expire = datetime.utcnow() + expires_delta
	else:
		expire = datetime.utcnow() + timedelta(
			minutes=Config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
		)
	
	to_encode.update({"exp": expire})
	encoded_jwt = jwt.encode(
		to_encode, 
		Config.JWT_SECRET_KEY, 
		algorithm=Config.JWT_ALGORITHM
	)
	return encoded_jwt


def verify_jwt_token(token: str) -> dict:
	"""
	Verifica un token JWT interno.
	Retorna el payload si es válido, diccionario vacío si es inválido.
	"""
	try:
		payload = jwt.decode(
			token, 
			Config.JWT_SECRET_KEY, 
			algorithms=[Config.JWT_ALGORITHM]
		)
		return payload
	except jwt.PyJWTError:
		return {}