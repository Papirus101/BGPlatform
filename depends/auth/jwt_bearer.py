from typing import Optional

from fastapi import Request, HTTPException
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param

from depends.auth.jwt_handler import decodeJWT

import settings

class OAuth2PasswordBearerCookie(OAuth2):
    def __init__(
            self,
            auto_error: bool = True,
    ):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        print(settings.DEBUG)
        if settings.DEBUG:
            cookie_authorization: str = request.headers.get("Authorization")
        else:
            cookie_authorization: str = request.cookies.get("Authorization")
        
        cookie_scheme, cookie_param = get_authorization_scheme_param(
            cookie_authorization
        )

        authorization = False
        scheme = None
        param = None
        valid = False

        if cookie_scheme.lower() == "bearer":
            authorization = True
            scheme = cookie_scheme
            param = cookie_param
            valid = await decodeJWT(param)

        else:
            authorization = False

        if not authorization or scheme.lower() != "bearer" or valid is None:
            if self.auto_error:
                raise HTTPException(
                    status_code=403, detail="Not authenticated"
                )
            else:
                return None
        return None
