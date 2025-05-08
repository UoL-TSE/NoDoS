import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from db import DB


class _AuthHandler():
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret = 'SECRET'

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def encode_token(self, user_id: int):
        payload = {
            'exp': datetime.utcnow() + timedelta(days=1, minutes=0),
            'iat': datetime.utcnow(),
            'sub': str(user_id)
        }
        return jwt.encode(
            payload,
            self.secret,
            algorithm='HS256'
        )

    def decode_token(self, token) -> int:

        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            user_id = int(payload['sub'])

            db = DB()
            if not db.get_user(user_id):
                raise HTTPException(status_code=401, detail='User not found')
            
            return user_id
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Token expired')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid token')

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials)   


auth_handler = _AuthHandler()
