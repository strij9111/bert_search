Feature: Search by filters

  Scenario: Search for Breaking bad
    Given request with text: "во все тяжкие"
    When send GET request
    Then response is OK
      And "top" items "title" match patterns: "^во все тяжкие"
      And "middle" items "title" match patterns: "все тяжк"
      And "middle" items "title" does not match patterns: "^во все тяжкие"
      And "bottom" items "description" match patterns: "все тяжк"
      And "bottom" items "title" does not match patterns: "все тяжк"

  Scenario: Search movies with Billy Bean
    Given request with text: "били бина"
    When send GET request
    Then response is OK
      And "top" items "title" match patterns: "Человек, который изменил всё"

  Scenario: Search movies with ski jumping
	Given request with text: "прыжки на лыжах"
    When send GET request
    Then response is OK
      And "top" items "title" match patterns: "Эдди \"Орел\""

  Scenario: Search actions with John Travolta
	Given request with text: "Боевики с Джоном Траволта"
    When send GET request
    Then response is OK
      And "top" items "title" match patterns: "Криминальное чтиво"

  Scenario: Search for "Replicants"
    Given request with text: "репликанты"
    When send GET request
    Then response is OK
      And "top" items "title" match patterns: "репликант"
      And "middle" items "description" match patterns: "репликант"

  Scenario: Search for "Forest Gump"
    Given request with text: "форрест гамп"
    When send GET request
    Then response is OK
      And "top" items "title" match patterns: "^форрест гамп$"

  Scenario: Search for movie with Spider man
    Given request with text: "человек паук"
    When send GET request
    Then response is OK
      And "top" items "title" match patterns: "^человек-паук$"
      And "middle" items "title" match patterns: "человек-паук"
      And "middle" items "title" does not match patterns: "^человек-паук$"
      And "bottom" items "description" match patterns: "человек,паук"
      And "bottom" items "title" does not match patterns: "человек-паук"

  Scenario: Search "Green book" by description
    Given request with text: "путешествие негра и белого"
    When send GET request
    Then response is OK
      And "top" items "title" match patterns: "^Зеленая книга$|^Зелёная книга$"
