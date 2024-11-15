import logging
from inspect import isawaitable
from functools import wraps

from quart import make_response, request
from werkzeug.datastructures import WWWAuthenticate

from common.config import SECRETS

LOG = logging.getLogger(__name__)

def require_token(f):
    @wraps(f)
    async def inner(*args, **kwargs):
        if (request.authorization is None
                or request.authorization.token is None):
            response = await make_response('Authorization token not found', 401)
            response.www_authenticate = WWWAuthenticate('Bearer')
            return response

        # timing side channel oops
        if request.authorization.token != SECRETS['server_token']:
            response = await make_response('Incorrect authorization token', 401)
            response.www_authenticate = WWWAuthenticate('Bearer')
            return response
        
        res = f(*args, **kwargs)
        if isawaitable(res):
            res = await res
        return res
    return inner
