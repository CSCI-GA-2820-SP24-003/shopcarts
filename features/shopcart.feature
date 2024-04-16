Feature: The shopcart service back-end
    As a Shopcart Manager
    I need a RESTful catalog service
    So that I can keep track of all the shopcarts

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Shopcart Demo RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Shopcart
    When I visit the "Home Page"
    And I set the "User_id" to "111"
    And I set the "Name" to "test"
    And I set the "Total_price" to "100.12"
    And I select "ACTIVE" in the "Status" dropdown
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "User_id" field should be empty
    And the "Name" field should be empty
    And the "Total_price" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "111" in the "user_id" field
    And I should see "test" in the "name" field
    And I should see "100.12" in the "Total_price" field
    And I should see "ACTIVE" in the "Status" dropdown