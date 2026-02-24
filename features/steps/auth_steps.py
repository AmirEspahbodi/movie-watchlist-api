# ═══════════════════════════════════════════════
# FILE: features/steps/auth_steps.py
# ═══════════════════════════════════════════════
from __future__ import annotations

from behave import given, then, when

from features.environment import run
from features.steps.common_steps import arun, create_user_async, login_user_async

# All auth DTOs live in this module
from src.models.dtos.auth.domain.v1.auth_domain_interface_dtos import (
    LoginInputDTOV1,
    RefreshTokenInputDTOV1,
    RegisterUserInputDTOV1,
)
from src.utils.jwt_utils import JWTUtils


# ── GIVEN steps ───────────────────────────────────────────────────────────────

@given("I am not registered")
def step_not_registered(context):
    """
    No-op: simply asserts we are starting from an empty state.
    before_scenario already clears all tables, so no user exists.
    """
    assert not context.users, "Expected no users registered, but context.users is not empty"


@given('a user "{email}" already exists')
def step_user_already_exists(context, email: str):
    """Create the user if they don't already exist in this scenario."""
    username = email.split("@")[0].replace(".", "_")
    arun(
        context,
        create_user_async(
            context,
            email=email,
            username=username,
            first_name="Test",
            last_name="User",
            password="TestPass123!",
        ),
    )


@given('a user "{email}" with password "{password}" exists')
def step_user_with_password_exists(context, email: str, password: str):
    """Create the user with the specified password."""
    username = email.split("@")[0].replace(".", "_")
    context.user_passwords[email] = password
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


@given('I have logged in as "{email}"')
def step_have_logged_in_as(context, email: str):
    """Log in as an existing user using their stored password (or default)."""
    password = context.user_passwords.get(email, "TestPass123!")
    arun(context, login_user_async(context, email, password))


# ── WHEN steps ────────────────────────────────────────────────────────────────

@when(
    'I register with email "{email}", username "{username}", '
    'first_name "{first_name}", last_name "{last_name}", password "{password}"'
)
def step_register(
    context,
    email: str,
    username: str,
    first_name: str,
    last_name: str,
    password: str,
):
    """Attempt to register a new user and capture result or error."""
    context.last_error = None
    context.last_result = None

    async def _do():
        input_dto = RegisterUserInputDTOV1(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        return await context.auth_logic.register_user(input_dto=input_dto)

    try:
        result = arun(context, _do())
        context.last_result = result
        context.users[email] = result.user_uuid
        context.user_passwords[email] = password
    except Exception as exc:
        context.last_error = exc


@when('I login with email "{email}" and password "{password}"')
def step_login(context, email: str, password: str):
    """Attempt to log in and capture result or error."""
    context.last_error = None
    context.last_result = None

    async def _do():
        input_dto = LoginInputDTOV1(email=email, password=password)
        return await context.auth_logic.login(input_dto=input_dto)

    try:
        result = arun(context, _do())
        context.last_result = result
        context.current_access_token = result.access_token
        context.current_refresh_token = result.refresh_token
    except Exception as exc:
        context.last_error = exc


@when("I call refresh with the refresh_token")
def step_refresh_token(context):
    """Exchange the current refresh_token for a new access_token."""
    context.last_error = None
    context.last_result = None

    async def _do():
        input_dto = RefreshTokenInputDTOV1(refresh_token=context.current_refresh_token)
        return await context.auth_logic.refresh_token(input_dto=input_dto)

    try:
        result = arun(context, _do())
        context.last_result = result
    except Exception as exc:
        context.last_error = exc


@when("I call get_me with the access_token")
def step_get_me(context):
    """Retrieve the current user profile using the stored access token."""
    context.last_error = None
    context.last_result = None

    async def _do():
        user_uuid = JWTUtils.get_user_uuid_from_token(
            context.current_access_token, expected_type="access"
        )
        return await context.auth_logic.get_me(user_uuid=user_uuid)

    try:
        result = arun(context, _do())
        context.last_result = result
    except Exception as exc:
        context.last_error = exc


# ── THEN / AND steps ─────────────────────────────────────────────────────────

@then("registration succeeds")
def step_registration_succeeds(context):
    assert context.last_error is None, (
        f"Expected registration to succeed, but got error: {context.last_error}"
    )
    assert context.last_result is not None, "Expected a result from registration but got None"


@then('the returned user has email "{email}"')
def step_returned_user_email(context, email: str):
    assert context.last_result.email == email, (
        f"Expected email '{email}', got '{context.last_result.email}'"
    )


@then("the returned user is_active is True")
def step_returned_user_is_active(context):
    assert context.last_result.is_active is True, (
        f"Expected is_active=True, got {context.last_result.is_active}"
    )


@then("I receive an access_token and a refresh_token")
def step_received_tokens(context):
    assert context.last_result.access_token is not None, "access_token is None"
    assert context.last_result.refresh_token is not None, "refresh_token is None"


@then('the token_type is "{token_type}"')
def step_token_type(context, token_type: str):
    assert context.last_result.token_type == token_type, (
        f"Expected token_type='{token_type}', got '{context.last_result.token_type}'"
    )


@then("I receive a new access_token")
def step_receive_new_access_token(context):
    assert context.last_result.access_token is not None, "New access_token is None"


@then('the profile email is "{email}"')
def step_profile_email(context, email: str):
    assert context.last_result.email == email, (
        f"Expected profile email '{email}', got '{context.last_result.email}'"
    )


@then("the profile is_active is True")
def step_profile_is_active(context):
    assert context.last_result.is_active is True, (
        f"Expected profile is_active=True, got {context.last_result.is_active}"
    )
