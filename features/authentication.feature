# ═══════════════════════════════════════════════
# FILE: features/authentication.feature
# ═══════════════════════════════════════════════
Feature: User Authentication
  As a visitor or registered user
  I want to register, log in, refresh tokens, and view my profile
  So that I can securely access the platform

  Scenario: Successfully register a new user
    Given I am not registered
    When I register with email "alice@test.com", username "alice", first_name "Alice", last_name "Smith", password "Password123!"
    Then registration succeeds
    And the returned user has email "alice@test.com"
    And the returned user is_active is True

  Scenario: Duplicate email registration is rejected
    Given a user "bob@test.com" already exists
    When I register with email "bob@test.com", username "bob2", first_name "Bob", last_name "Jones", password "Password123!"
    Then I should receive an AlreadyExistsError

  Scenario: Login with valid credentials returns tokens
    Given a user "carol@test.com" with password "Secret456!" exists
    When I login with email "carol@test.com" and password "Secret456!"
    Then I receive an access_token and a refresh_token
    And the token_type is "bearer"

  Scenario: Login with wrong password is rejected
    Given a user "dave@test.com" with password "CorrectPass1!" exists
    When I login with email "dave@test.com" and password "WrongPass1!"
    Then I should receive an UnauthenticatedError

  Scenario: Refresh token issues a new access token
    Given a user "eve@test.com" with password "Evelyn789!" exists
    And I have logged in as "eve@test.com"
    When I call refresh with the refresh_token
    Then I receive a new access_token
    And the token_type is "bearer"

  Scenario: Get current user profile (me)
    Given a user "frank@test.com" with password "Frank000!" exists
    And I have logged in as "frank@test.com"
    When I call get_me with the access_token
    Then the profile email is "frank@test.com"
    And the profile is_active is True
