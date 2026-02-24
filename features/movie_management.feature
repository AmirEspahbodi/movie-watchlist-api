# ═══════════════════════════════════════════════
# FILE: features/movie_management.feature
# ═══════════════════════════════════════════════
Feature: Movie Management
  As an admin
  I want to manage genres and movies
  So that users can browse and track the catalog

  Background:
    Given I am logged in as admin "admin@test.com"

  Scenario: Admin creates a genre
    When I create a genre named "Science Fiction" with description "Sci-Fi films"
    Then the genre is created with name "Science Fiction"
    And the genre has a valid genre_uuid

  Scenario: Duplicate genre name is rejected
    Given a genre "Drama" already exists
    When I create a genre named "Drama" with no description
    Then I should receive an AlreadyExistsError

  Scenario: Admin creates a movie linked to a genre
    Given a genre "Action" exists
    When I create a movie titled "Die Hard" in genre "Action" with description "An action classic"
    Then the movie is created with title "Die Hard"
    And the movie has the correct genre_uuid

  Scenario: Search movies returns paginated results
    Given a genre "Thriller" exists
    And a genre "Comedy" exists
    And movie "Se7en" in genre "Thriller" exists
    And movie "Airplane!" in genre "Comedy" exists
    When I search movies with page 1 and page_size 10
    Then I receive at least 2 movies in the results

  Scenario: Search movies filtered by genre
    Given a genre "Horror" exists
    And movie "The Shining" in genre "Horror" exists
    And a genre "Animation" exists
    And movie "Toy Story" in genre "Animation" exists
    When I search movies filtered by genre "Horror"
    Then I receive exactly 1 movie
    And the movie title is "The Shining"

  Scenario: Admin updates a movie description
    Given a genre "Western" exists
    And movie "Unforgiven" in genre "Western" exists
    When I update movie "Unforgiven" description to "Clint Eastwood classic"
    Then the movie description is "Clint Eastwood classic"

  Scenario: Admin deletes a movie
    Given a genre "Musical" exists
    And movie "Grease" in genre "Musical" exists
    When I delete movie "Grease"
    Then fetching movie "Grease" raises NotFoundError
