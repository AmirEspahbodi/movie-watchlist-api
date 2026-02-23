from archipy.helpers.utils.base_utils import BaseUtils
from archipy.models.errors import InvalidArgumentError, UnauthenticatedError, UnavailableError, UnknownError
from fastapi import FastAPI

from src.controllers.auth.v1 import auth_controller
from src.controllers.genre.v1 import genre_controller
from src.controllers.movie.v1 import movie_controller
from src.controllers.rating.v1 import rating_controller
from src.controllers.user.v1 import user_controller
from src.controllers.watch.v1 import watch_controller


def set_dispatch_routes(app: FastAPI) -> None:
    common_private_response = BaseUtils.get_fastapi_exception_responses(
        [UnauthenticatedError, UnknownError, UnavailableError, InvalidArgumentError],
    )
    app.include_router(router=user_controller.routerV1, prefix="/api/v1/users", responses=common_private_response)
    app.include_router(router=auth_controller.routerV1, prefix="/api/v1/auth", responses=common_private_response)
    app.include_router(router=genre_controller.routerV1, prefix="/api/v1/genres", responses=common_private_response)
    app.include_router(router=movie_controller.routerV1, prefix="/api/v1/movies", responses=common_private_response)
    app.include_router(router=watch_controller.routerV1, prefix="/api/v1/watchlist", responses=common_private_response)
    app.include_router(router=rating_controller.routerV1, prefix="/api/v1/ratings", responses=common_private_response)
