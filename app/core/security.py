# app/core/security.py
import hashlib
import base64
import uuid
from datetime import datetime, timezone
import jwt
from typing import Optional
from datetime import timedelta

from app.config import Config

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