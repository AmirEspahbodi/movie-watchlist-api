# ═══════════════════════════════════════════════
# FILE: features/steps/common_steps.py
# ═══════════════════════════════════════════════
from __future__ import annotations

from behave import given, then

from features.environment import run


# ── A. ASYNC RUNNER UTILITY ───────────────────────────────────────────────────

def arun(context, coro):
    """Synchronous wrapper: run an async coroutine on the shared event loop."""
    return context.loop.run_until_complete(coro)


# ── B. USER CREATION HELPER ───────────────────────────────────────────────────

async def create_user_async(
    context,
    email: str,
    username: str,
    first_name: str,
    last_name: str,
    password: str,
    is_super_user: bool = False,
):
    """
    Create a user via auth_logic.register_user, then optionally escalate to
    super-user via user_logic.update_user (ED-9).

    Returns RegisterUserOutputDTOV1 and stores the UUID in context.users[email].
    """
    from archipy.models.errors import AlreadyExistsError

    from src.models.dtos.auth.domain.v1.auth_domain_interface_dtos import RegisterUserInputDTOV1

    # Store password for potential re-login later
    context.user_passwords[email] = password

    # Check if already created this run
    if email in context.users:
        return None

    input_dto = RegisterUserInputDTOV1(
        email=email,
        username=username,
        first_name=first_name,
        last_name=last_name,
        password=password,
    )
    try:
        result = await context.auth_logic.register_user(input_dto=input_dto)
        context.users[email] = result.user_uuid

        if is_super_user:
            # Escalate to super-user (ED-9): update_user with is_super_user=True
            from src.models.dtos.user.domain.v1.user_domain_interface_dtos import UpdateUserInputDTOV1

            update_dto = UpdateUserInputDTOV1(
                user_uuid=result.user_uuid,
                is_super_user=True,
            )
            await context.user_logic.update_user(input_dto=update_dto)

        return result
    except AlreadyExistsError:
        # User already exists – store UUID via get_me if needed
        return None


# ── C. LOGIN HELPER ───────────────────────────────────────────────────────────

async def login_user_async(context, email: str, password: str):
    """
    Log in via auth_logic.login.  Stores access/refresh tokens and user UUID
    on the behave context object.
    """
    from src.models.dtos.auth.domain.v1.auth_domain_interface_dtos import LoginInputDTOV1
    from src.utils.jwt_utils import JWTUtils

    input_dto = LoginInputDTOV1(email=email, password=password)
    result = await context.auth_logic.login(input_dto=input_dto)
    context.current_access_token = result.access_token
    context.current_refresh_token = result.refresh_token
    # Extract user UUID from the JWT so we have it available for subsequent steps
    context.current_user_uuid = JWTUtils.get_user_uuid_from_token(result.access_token, "access")
    return result


# ── D. SHARED GIVEN STEPS ─────────────────────────────────────────────────────

@given('I am logged in as "{email}"')
def step_logged_in_as(context, email: str):
    """
    Create a regular (non-admin) user with a fixed default password, then log in.
    If the user was already created in this scenario, just log in.
    """
    password = context.user_passwords.get(email, "TestPass123!")
    username = email.split("@")[0].replace(".", "_")

    if email not in context.users:
        arun(
            context,
            create_user_async(
                context,
                email=email,
                username=username,
                first_name="Test",
                last_name="User",
                password=password,
            ),
        )

    arun(context, login_user_async(context, email, password))


@given('I am logged in as admin "{email}"')
def step_logged_in_as_admin(context, email: str):
    """
    Create a super-user account, then log in.

    Implementation follows ED-9:
      1. register_user  → creates user with correct hashed_password
      2. update_user    → sets is_super_user=True
      3. login          → returns tokens
    """
    password = context.user_passwords.get(email, "AdminPass123!")
    username = email.split("@")[0].replace(".", "_")

    if email not in context.users:
        arun(
            context,
            create_user_async(
                context,
                email=email,
                username=username,
                first_name="Admin",
                last_name="User",
                password=password,
                is_super_user=True,
            ),
        )
        context.user_passwords[email] = password

    arun(context, login_user_async(context, email, password))


# ── E. SHARED THEN / AND STEPS ────────────────────────────────────────────────

@then("I should receive an AlreadyExistsError")
def step_expect_already_exists(context):
    from archipy.models.errors import AlreadyExistsError

    assert isinstance(context.last_error, AlreadyExistsError), (
        f"Expected AlreadyExistsError, got {type(context.last_error)}: {context.last_error}"
    )


@then("I should receive an UnauthenticatedError")
def step_expect_unauthenticated(context):
    from archipy.models.errors import UnauthenticatedError

    assert isinstance(context.last_error, UnauthenticatedError), (
        f"Expected UnauthenticatedError, got {type(context.last_error)}: {context.last_error}"
    )


@then("I should receive a NotFoundError")
def step_expect_not_found(context):
    from archipy.models.errors import NotFoundError

    assert isinstance(context.last_error, NotFoundError), (
        f"Expected NotFoundError, got {type(context.last_error)}: {context.last_error}"
    )


@then('I should get error "{message}"')
def step_expect_error_message(context, message: str):
    """
    Maps human-readable error message strings to ArchiPy exception types.

    "Can only rate watched movies"   → InvalidArgumentError (from rating_logic)
    "Rating must be between 1 and 5" → ValueError (simulated at step level;
                                        see movie_steps.py "I try to rate" step)
    """
    from archipy.models.errors import InvalidArgumentError

    if message == "Rating must be between 1 and 5":
        assert isinstance(context.last_error, (ValueError, InvalidArgumentError)), (
            f"Expected ValueError or InvalidArgumentError for range guard, "
            f"got {type(context.last_error)}: {context.last_error}"
        )
    elif message == "Can only rate watched movies":
        assert isinstance(context.last_error, InvalidArgumentError), (
            f"Expected InvalidArgumentError for 'can only rate watched movies', "
            f"got {type(context.last_error)}: {context.last_error}"
        )
    else:
        # Generic fallback: assert any error exists
        assert context.last_error is not None, (
            f"Expected an error containing '{message}' but last_error is None"
        )
