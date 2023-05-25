Feature: Test API response

    Requests to the root of the api
    check correct answer

  Scenario: Search for "Matrix"
    Given request with text: "Матрица"
    When send GET request
    Then response is OK
      And "top" items "title" match patterns: "^матрица$"
      And "middle" items "title" match patterns: "матриц"
      And "middle" items "title" does not match patterns: "^матрица$"
      And "bottom" items "description" match patterns: "матриц"
      And "bottom" items "title" does not match patterns: "матриц"


  Scenario: Search for "Lord of the Rings"
    Given request with text: "Властелин колец"
    When send GET request
    Then response is OK
      And "top" items "title" match patterns: "властелин колец"
      And "middle" items are sorted as:
          | title                 |
          | властелин             |
          | кольц\|колец          |
          | власт\|кольц\|колец   |
      And "middle" items "title" does not match patterns: "властелин колец"
      And "bottom" items "description" match patterns: "власт|кольц|колец"
      And "bottom" items "title" does not match patterns: "власт|кольц|колец"


  Scenario: Search for "Twin Peaks"
    Given request with text: "Твин Пикс"
    When send GET request
    Then response is OK
      And "top" items "title" match patterns: "^твин пикс$"
      And "middle" items "title" match patterns: "твин пикс"
      And "middle" items "title" does not match patterns: "^твин пикс$"
      And "bottom" items "description" match patterns: "\bтвин пикс\w*\b"
      And "bottom" items "title" does not match patterns: "твин пикс"


  Scenario: Search for Stephen King
    Given request with text: "по Стивену Кингу"
    When send GET request
    Then response is OK
      And "top" items "description" match patterns: "стивен\w* кинг\w*"
      And "top" items "title" match patterns: "\bстивен\w* \bкинг\w*"
      And "middle" items "title" match patterns: "\bстивен\w*|\bкинг\w*"
      And "bottom" items "description" match patterns: "\bстивен\w*|\bкинг\w*"