Feature: The shopcart service back-end
    As a Shopcart Manager
    I need a RESTful catalog service
    So that I can keep track of all the shopcarts

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Shopcart Demo RESTful Service" in the title
    And I should not see "404 Not Found"
