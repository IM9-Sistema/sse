import importlib
from fastapi.routing import APIRouter
from uvicorn.logging import logging
import pathlib
import os

logger = logging.getLogger(__name__)


def get_routers(path: pathlib.Path = None) -> list[APIRouter]:
    file_path = pathlib.Path(__file__).parent.resolve()
    if not path:
        path = file_path

    routers = []
    for file in os.listdir(path):
        if file.startswith('__'):
            continue

        if os.path.isdir(path/file):
            r = APIRouter(prefix='/'+file)
            for router in get_routers(pathlib.Path(path/file)):
                r.include_router(router)
            routers.append(r)
            continue

        if file.endswith(".py"):
            file = file[:-3]
        commonprefix = os.path.commonprefix([file_path.parent, path])
        relative_path = os.path.relpath(path, commonprefix)
        lib = importlib.import_module('.'.join(relative_path.split(os.path.sep))+'.'+file)

        if hasattr(lib, 'router'):
            routers.append(lib.router)
    return routers

