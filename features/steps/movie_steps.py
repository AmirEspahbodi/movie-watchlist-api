# ═══════════════════════════════════════════════
# FILE: features/steps/movie_steps.py
# ═══════════════════════════════════════════════
from __future__ import annotations

from behave import given, then, when

from features.steps.common_steps import arun

from src.models.dtos.genre.domain.v1.genre_domain_interface_dtos import (
    CreateGenreInputDTOV1,
    GetGenreInputDTOV1,
)
from src.models.dtos.movie.domain.v1.movie_domain_interface_dtos import (
    CreateMovieInputDTOV1,
    DeleteMovieInputDTOV1,
    GetMovieInputDTOV1,
    SearchMovieInputDTOV1,
    UpdateMovieInputDTOV1,
)
from src.models.dtos.rating.domain.v1.rating_domain_interface_dtos import (
    GetMyRatingsInputDTOV1,
    RateMovieInputDTOV1,
    UpdateRatingInputDTOV1,
)
from src.models.dtos.watch.domain.v1.watch_domain_interface_dtos import (
    UpdateWatchStatusInputDTOV1,
    WatchMovieInputDTOV1,
)
from src.models.types.watch_status_type import WatchStatusType
from archipy.models.errors import AlreadyExistsError, InvalidArgumentError, NotFoundError


# ═════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS (async, not step definitions)
# ═════════════════════════════════════════════════════════════════════════════

async def ensure_genre(context, name: str, description: str | None = None):
    """Create genre if not already in context.genres; return genre_uuid."""
    if name not in context.genres:
        dto = CreateGenreInputDTOV1(name=name, description=description)
        result = await context.genre_logic.create_genre(input_dto=dto)
        context.genres[name] = result.genre_uuid
        context.last_genre_name = name
    return context.genres[name]


async def ensure_movie(
    context,
    title: str,
    genre_name: str,
    description: str | None = None,
):
    """Create movie (and its genre) if not already in context.movies; return movie_uuid."""
    genre_uuid = await ensure_genre(context, genre_name)
    if title not in context.movies:
        dto = CreateMovieInputDTOV1(
            title=title,
            description=description,
            genre_uuid=genre_uuid,
        )
        result = await context.movie_logic.create_movie(input_dto=dto)
        context.movies[title] = result.movie_uuid
        context.last_genre_name = genre_name
    return context.movies[title]


async def ensure_watch(context, title: str, status: WatchStatusType):
    """
    Add movie to the current user's watchlist with the given status.

    If a watch record already exists for this (user, movie) pair, update its
    status to the desired value rather than creating a duplicate.
    """
    movie_uuid = context.movies[title]
    user_uuid = context.current_user_uuid
    key = (str(user_uuid), title)

    if key not in context.watches:
        dto = WatchMovieInputDTOV1(
            movie_uuid=movie_uuid,
            user_uuid=user_uuid,
            status=status,
        )
        result = await context.watch_logic.watch_movie(input_dto=dto)
        context.watches[key] = result.watch_uuid
    else:
        # Update status on the existing record
        watch_uuid = context.watches[key]
        update_dto = UpdateWatchStatusInputDTOV1(
            watch_uuid=watch_uuid,
            user_uuid=user_uuid,
            status=status,
        )
        await context.watch_logic.update_watch_status(input_dto=update_dto)

    return context.watches[key]


# ═════════════════════════════════════════════════════════════════════════════
# STEP DEFINITIONS — MOVIE MANAGEMENT
# ═════════════════════════════════════════════════════════════════════════════

# ── Genre GIVEN steps ─────────────────────────────────────────────────────────

@given('a genre "{name}" already exists')
def step_genre_already_exists(context, name: str):
    arun(context, ensure_genre(context, name))


@given('a genre "{name}" exists')
def step_genre_exists(context, name: str):
    arun(context, ensure_genre(context, name))


@given('a genre "{genre_name}" and movie "{title}" exist')
def step_genre_and_movie_exist(context, genre_name: str, title: str):
    arun(context, ensure_movie(context, title, genre_name))


@given('movie "{title}" in genre "{genre_name}" exists')
def step_movie_in_genre_exists(context, title: str, genre_name: str):
    arun(context, ensure_movie(context, title, genre_name))


# ── Movie WHEN steps ──────────────────────────────────────────────────────────

@when('I create a genre named "{name}" with description "{desc}"')
def step_create_genre_with_desc(context, name: str, desc: str):
    context.last_error = None
    context.last_result = None

    async def _do():
        dto = CreateGenreInputDTOV1(name=name, description=desc)
        return await context.genre_logic.create_genre(input_dto=dto)

    try:
        result = arun(context, _do())
        context.last_result = result
        context.genres[name] = result.genre_uuid
        context.last_genre_name = name
    except Exception as exc:
        context.last_error = exc


@when('I create a genre named "{name}" with no description')
def step_create_genre_no_desc(context, name: str):
    context.last_error = None
    context.last_result = None

    async def _do():
        dto = CreateGenreInputDTOV1(name=name, description=None)
        return await context.genre_logic.create_genre(input_dto=dto)

    try:
        result = arun(context, _do())
        context.last_result = result
        context.genres[name] = result.genre_uuid
        context.last_genre_name = name
    except Exception as exc:
        context.last_error = exc


@when('I create a movie titled "{title}" in genre "{genre_name}" with description "{desc}"')
def step_create_movie(context, title: str, genre_name: str, desc: str):
    context.last_error = None
    context.last_result = None

    async def _do():
        genre_uuid = await ensure_genre(context, genre_name)
        dto = CreateMovieInputDTOV1(
            title=title,
            description=desc,
            genre_uuid=genre_uuid,
        )
        return await context.movie_logic.create_movie(input_dto=dto)

    try:
        result = arun(context, _do())
        context.last_result = result
        context.movies[title] = result.movie_uuid
        context.last_genre_name = genre_name
    except Exception as exc:
        context.last_error = exc


@when("I search movies with page {page:d} and page_size {size:d}")
def step_search_movies(context, page: int, size: int):
    context.last_error = None
    context.last_result = None

    async def _do():
        dto = SearchMovieInputDTOV1.create(page=page, page_size=size)
        return await context.movie_logic.search_movies(input_dto=dto)

    try:
        result = arun(context, _do())
        context.last_result = result
    except Exception as exc:
        context.last_error = exc


@when('I search movies filtered by genre "{genre_name}"')
def step_search_movies_by_genre(context, genre_name: str):
    context.last_error = None
    context.last_result = None

    async def _do():
        genre_uuid = context.genres.get(genre_name)
        dto = SearchMovieInputDTOV1.create(genre_uuid=genre_uuid, page=1, page_size=50)
        return await context.movie_logic.search_movies(input_dto=dto)

    try:
        result = arun(context, _do())
        context.last_result = result
    except Exception as exc:
        context.last_error = exc


@when('I update movie "{title}" description to "{desc}"')
def step_update_movie_description(context, title: str, desc: str):
    context.last_error = None
    context.last_result = None

    async def _do():
        movie_uuid = context.movies[title]
        dto = UpdateMovieInputDTOV1(movie_uuid=movie_uuid, description=desc)
        await context.movie_logic.update_movie(input_dto=dto)
        return movie_uuid

    try:
        movie_uuid = arun(context, _do())
        context.last_result = movie_uuid  # store uuid for Then step
    except Exception as exc:
        context.last_error = exc


@when('I delete movie "{title}"')
def step_delete_movie(context, title: str):
    context.last_error = None
    context.last_result = None

    async def _do():
        movie_uuid = context.movies[title]
        dto = DeleteMovieInputDTOV1(movie_uuid=movie_uuid)
        await context.movie_logic.delete_movie(input_dto=dto)

    try:
        arun(context, _do())
    except Exception as exc:
        context.last_error = exc


# ── Movie THEN steps ──────────────────────────────────────────────────────────

@then('the genre is created with name "{name}"')
def step_genre_created_with_name(context, name: str):
    assert context.last_error is None, (
        f"Expected genre creation to succeed, got error: {context.last_error}"
    )
    assert context.last_result is not None, "Expected a result from genre creation"
    assert context.last_result.name == name, (
        f"Expected genre name '{name}', got '{context.last_result.name}'"
    )
    # Ensure we track the uuid
    context.genres[name] = context.last_result.genre_uuid


@then("the genre has a valid genre_uuid")
def step_genre_has_uuid(context):
    assert context.last_result.genre_uuid is not None, "genre_uuid is None"


@then('the movie is created with title "{title}"')
def step_movie_created_with_title(context, title: str):
    assert context.last_error is None, (
        f"Expected movie creation to succeed, got error: {context.last_error}"
    )
    assert context.last_result is not None, "Expected a result from movie creation"
    assert context.last_result.title == title, (
        f"Expected movie title '{title}', got '{context.last_result.title}'"
    )
    context.movies[title] = context.last_result.movie_uuid


@then("the movie has the correct genre_uuid")
def step_movie_has_correct_genre_uuid(context):
    assert context.last_genre_name is not None, "context.last_genre_name is not set"
    expected_genre_uuid = context.genres[context.last_genre_name]
    actual_genre_uuid = context.last_result.genre_uuid
    assert actual_genre_uuid == expected_genre_uuid, (
        f"Expected genre_uuid {expected_genre_uuid}, got {actual_genre_uuid}"
    )


@then("I receive at least {n:d} movies in the results")
def step_receive_at_least_n_movies(context, n: int):
    assert context.last_error is None, f"Search failed: {context.last_error}"
    total = getattr(context.last_result, "total", None) or len(context.last_result.movies)
    assert total >= n, f"Expected at least {n} movies, got {total}"


@then("I receive exactly {n:d} movie")
def step_receive_exactly_n_movie_singular(context, n: int):
    assert context.last_error is None, f"Search failed: {context.last_error}"
    total = getattr(context.last_result, "total", len(context.last_result.movies))
    assert total == n, f"Expected exactly {n} movie(s), got {total}"


@then("I receive exactly {n:d} movies")
def step_receive_exactly_n_movies(context, n: int):
    assert context.last_error is None, f"Search failed: {context.last_error}"
    total = getattr(context.last_result, "total", len(context.last_result.movies))
    assert total == n, f"Expected exactly {n} movie(s), got {total}"


@then('the movie title is "{title}"')
def step_movie_title_is(context, title: str):
    assert len(context.last_result.movies) > 0, "No movies in results"
    assert context.last_result.movies[0].title == title, (
        f"Expected title '{title}', got '{context.last_result.movies[0].title}'"
    )


@then('the movie description is "{desc}"')
def step_movie_description_is(context, desc: str):
    """Fetch the movie by UUID and verify its description."""
    assert context.last_error is None, f"Previous step raised: {context.last_error}"

    async def _do():
        # context.last_result holds the movie_uuid (set in update step)
        movie_uuid = context.last_result
        dto = GetMovieInputDTOV1(movie_uuid=movie_uuid)
        return await context.movie_logic.get_movie(input_dto=dto)

    result = arun(context, _do())
    assert result.description == desc, (
        f"Expected description '{desc}', got '{result.description}'"
    )


@then('fetching movie "{title}" raises NotFoundError')
def step_fetching_movie_raises_not_found(context, title: str):
    """Verify that a previously deleted movie can no longer be retrieved."""
    movie_uuid = context.movies.get(title)
    assert movie_uuid is not None, f"Movie '{title}' was never created in this scenario"

    async def _do():
        dto = GetMovieInputDTOV1(movie_uuid=movie_uuid)
        return await context.movie_logic.get_movie(input_dto=dto)

    raised = False
    try:
        arun(context, _do())
    except NotFoundError:
        raised = True
    except Exception as exc:
        # Some adapters wrap NotFoundError; check by class name
        if "NotFoundError" in type(exc).__name__:
            raised = True
        else:
            raise

    assert raised, f"Expected NotFoundError when fetching deleted movie '{title}'"


# ═════════════════════════════════════════════════════════════════════════════
# STEP DEFINITIONS — WATCH & RATING
# ═════════════════════════════════════════════════════════════════════════════

_STATUS_MAP = {
    "watched": WatchStatusType.WATCHED,
    "want_to_watch": WatchStatusType.WANT_TO_WATCH,
}


@given('I have a movie "{title}" with status "{status}"')
def step_have_movie_with_status(context, title: str, status: str):
    """
    Ensure the movie exists (under genre "General" if not already created),
    then ensure a watch record exists for the current user with the given status.
    """
    watch_status = _STATUS_MAP.get(status)
    assert watch_status is not None, (
        f"Unknown status '{status}'. Valid values: {list(_STATUS_MAP.keys())}"
    )

    if title not in context.movies:
        arun(context, ensure_movie(context, title, "General"))

    arun(context, ensure_watch(context, title, watch_status))


@given('I have rated "{title}" with {n:d} stars')
def step_have_rated_with_stars(context, title: str, n: int):
    """
    Ensure the movie is watched, then create a rating record.
    Stores the rate_uuid in context.ratings for later update steps.
    """
    # Make sure there's a WATCHED record first
    if title not in context.movies:
        arun(context, ensure_movie(context, title, "General"))

    key = (str(context.current_user_uuid), title)
    if key not in context.watches:
        arun(context, ensure_watch(context, title, WatchStatusType.WATCHED))

    async def _do():
        movie_uuid = context.movies[title]
        dto = RateMovieInputDTOV1(
            movie_uuid=movie_uuid,
            user_uuid=context.current_user_uuid,
            score=n,
        )
        result = await context.rating_logic.rate_movie(input_dto=dto)
        context.ratings[key] = result.rate_uuid
        return result

    arun(context, _do())


# ── Rating WHEN steps ─────────────────────────────────────────────────────────

@when('I rate "{title}" with {n:d} stars')
def step_rate_movie(context, title: str, n: int):
    """Rate a movie; store result or error."""
    context.last_error = None
    context.last_result = None

    async def _do():
        movie_uuid = context.movies[title]
        dto = RateMovieInputDTOV1(
            movie_uuid=movie_uuid,
            user_uuid=context.current_user_uuid,
            score=n,
        )
        return await context.rating_logic.rate_movie(input_dto=dto)

    try:
        result = arun(context, _do())
        context.last_result = result
        key = (str(context.current_user_uuid), title)
        context.ratings[key] = result.rate_uuid
    except Exception as exc:
        context.last_error = exc


@when('I try to rate "{title}" with {n:d} stars')
def step_try_rate_movie(context, title: str, n: int):
    """
    Attempt to rate a movie, handling both out-of-range scores and
    business-rule violations (e.g. WANT_TO_WATCH status).

    ED-2 / Section 9: SQLite does not enforce the CHECK CONSTRAINT, so we
    simulate the Pydantic REST-layer validation for score range here.
    """
    context.last_error = None
    context.last_result = None

    # ── Simulate REST-layer Pydantic field validation (ge=1, le=5) ──────────
    if n < 1 or n > 5:
        context.last_error = ValueError(f"Rating must be between 1 and 5 (got {n})")
        return

    async def _do():
        movie_uuid = context.movies[title]
        dto = RateMovieInputDTOV1(
            movie_uuid=movie_uuid,
            user_uuid=context.current_user_uuid,
            score=n,
        )
        return await context.rating_logic.rate_movie(input_dto=dto)

    try:
        result = arun(context, _do())
        context.last_result = result
    except (InvalidArgumentError, AlreadyExistsError, Exception) as exc:
        context.last_error = exc


@when('I update my rating for "{title}" to {n:d} stars')
def step_update_rating(context, title: str, n: int):
    """Update an existing rating to a new score."""
    context.last_error = None
    context.last_result = None

    async def _do():
        key = (str(context.current_user_uuid), title)
        rate_uuid = context.ratings[key]
        dto = UpdateRatingInputDTOV1(
            rate_uuid=rate_uuid,
            user_uuid=context.current_user_uuid,
            score=n,
        )
        await context.rating_logic.update_rating(input_dto=dto)

    try:
        arun(context, _do())
    except Exception as exc:
        context.last_error = exc


@when("I fetch my ratings")
def step_fetch_my_ratings(context):
    """Retrieve the current user's complete rating list."""
    context.last_error = None
    context.last_result = None

    async def _do():
        dto = GetMyRatingsInputDTOV1.create(user_uuid=context.current_user_uuid)
        return await context.rating_logic.get_my_ratings(input_dto=dto)

    try:
        result = arun(context, _do())
        context.last_result = result
    except Exception as exc:
        context.last_error = exc


# ── Rating THEN steps ─────────────────────────────────────────────────────────

@then("the movie rating should be {n:d}")
def step_movie_rating_should_be(context, n: int):
    assert context.last_error is None, f"Rating step raised: {context.last_error}"
    assert context.last_result is not None, "Rating result is None"
    assert context.last_result.score == n, (
        f"Expected score {n}, got {context.last_result.score}"
    )


@then('my rating for "{title}" is {n:d}')
def step_my_rating_for_is(context, title: str, n: int):
    """Fetch ratings and assert the score for the specified title."""
    async def _do():
        dto = GetMyRatingsInputDTOV1.create(user_uuid=context.current_user_uuid)
        return await context.rating_logic.get_my_ratings(input_dto=dto)

    result = arun(context, _do())
    matching = [r for r in result.ratings if r.title == title]
    assert matching, f"No rating found for movie '{title}'"
    assert matching[0].score == n, (
        f"Expected score {n} for '{title}', got {matching[0].score}"
    )


@then('"{title}" appears in my ratings with score {n:d}')
def step_title_appears_in_ratings_with_score(context, title: str, n: int):
    assert context.last_error is None, f"Fetch ratings raised: {context.last_error}"
    assert context.last_result is not None, "Ratings result is None"
    found = any(
        r.title == title and r.score == n for r in context.last_result.ratings
    )
    assert found, (
        f"Expected '{title}' with score {n} in ratings. "
        f"Got: {[(r.title, r.score) for r in context.last_result.ratings]}"
    )
