# ═══════════════════════════════════════════════
# FILE: features/movie_rating.feature
# ═══════════════════════════════════════════════
Feature: Movie Rating
  As a user
  I want to rate movies I've watched
  So that I can track my opinions

  Background:
    Given I am logged in as "user@test.com"
    And I have a movie "The Matrix" with status "watched"

  Scenario: Rate a watched movie
    When I rate "The Matrix" with 5 stars
    Then the movie rating should be 5

  Scenario: Cannot rate an unwatched movie
    Given I have a movie "Inception" with status "want_to_watch"
    When I try to rate "Inception" with 5 stars
    Then I should get error "Can only rate watched movies"

  Scenario: Invalid rating value
    When I try to rate "The Matrix" with 6 stars
    Then I should get error "Rating must be between 1 and 5"

  Scenario: Update an existing rating
    Given I have rated "The Matrix" with 3 stars
    When I update my rating for "The Matrix" to 4 stars
    Then my rating for "The Matrix" is 4

  Scenario: Get my ratings returns correct list
    Given I have rated "The Matrix" with 5 stars
    When I fetch my ratings
    Then "The Matrix" appears in my ratings with score 5
