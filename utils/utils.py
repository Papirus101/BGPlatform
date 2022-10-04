import settings


async def get_user_token(request):
    if settings.DEBUG:
        token = request.headers.get("Authorization").split()
    else:
        _, token = request.cookies.get("Authorization").split()
    return token
