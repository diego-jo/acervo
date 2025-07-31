from http import HTTPStatus

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from books_collection.common.exception.errors import (
    DuplicatedRegistry,
    ForbidenOperation,
    RegistryNotFound,
)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    return JSONResponse(
        status_code=HTTPStatus.BAD_REQUEST, content={'detail': exc.errors()}
    )


async def duplicated_register_exception_handler(
    request: Request, exc: DuplicatedRegistry
):
    return JSONResponse(
        status_code=HTTPStatus.CONFLICT, content={'detail': exc.msg}
    )


async def registry_not_found_exception_handler(
        request: Request, exc: RegistryNotFound
):
    return JSONResponse(
        status_code=HTTPStatus.NOT_FOUND, content={'detail': exc.msg}
    )


async def forbiden_exception_handler(request: Request, exc: ForbidenOperation):
    return JSONResponse(
        status_code=HTTPStatus.FORBIDDEN, content={'detail': exc.msg}
    )

# TODO: entender se o exception handler segue uma ordem de declaração.
# ou seja, caso eu tenha uma exceção desconhecida sendo levantada, posso
# criar um handler que capture uma Exception geral?


exception_handlers = {
    RequestValidationError: validation_exception_handler,
    DuplicatedRegistry: duplicated_register_exception_handler,
    ForbidenOperation: forbiden_exception_handler,
}
