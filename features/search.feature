Feature: Search

  Scenario Outline: Search by text "<title>"
    Given request with text: "<title>"
    When send GET request
    Then response is OK
      And "top" items "title" match patterns: "^<title>$"
      And "middle" items "title" match patterns: "<middle keywords>"
      And "middle" items "title" does not match patterns: "^<title>$"
      And "bottom" items "description" match patterns: "<bottom keywords>"
      And "bottom" items "title" does not match patterns: "<bottom keywords>"

  Examples: Search cases
    | title                   | middle keywords   | bottom keywords     |
    | терминатор              | терминатор        | терминатор          |
    | друзья                  | друзья\|друг      | друзья\|друг        |
    | искатели                | искател           | искател             |
    | история игрушек         | история игрушек   | истор\|игруш\|игра  |
    | куколки                 | куколк            | куколк              |
    | (лед\|лёд)              | лед\|лёд          | лед\|лёд            |
    | тролли                  | тролл             | тролл               |
    | игры разума             | игр\|разум        | игр\|разум          |
    | мстители: эра альтрона  | мстители          | мстител             |
