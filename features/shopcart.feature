Feature: The shopcart service back-end
    As a Shopcart Manager
    I need a RESTful catalog service
    So that I can keep track of all the shopcarts

Background:
    Given the following shopcarts
        | user_id | name    | total_price    | status  |   
        | 1       | aa      | 1.00           | ACTIVE  | 
        | 2       | bb      | 2.00           | ACTIVE  |
        | 3       | cc      | 3.00           | ACTIVE  |
        | 4       | dd      | 4.00           | ACTIVE  | 

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

Scenario: List all shopcarts
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "aa" in the results
    And I should see "bb" in the results
    And I should see "cc" in the results
    And I should see "dd" in the results
    And I should not see "ee" in the results

Scenario: Delete a Shopcart
    When I visit the "Home Page"
    And I set the "User_id" to "6"
    And I set the "Name" to "ff"
    And I set the "Total_price" to "6.00"
    And I select "ACTIVE" in the "Status" dropdown
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Delete" button
    Then I should see the message "Shopcart has been Deleted!"
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "aa" in the results
    And I should see "bb" in the results
    And I should see "cc" in the results
    And I should see "dd" in the results
    And I should not see "ee" in the results

Scenario: Update a Shopcart
    When I visit the "Home Page"
    And I set the "User_id" to "5"
    And I set the "Name" to "ee"
    And I set the "Total_price" to "5.12"
    And I select "ACTIVE" in the "Status" dropdown
    And I press the "Create" button
    And I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I set the "User_id" to "5"
    And I set the "Name" to "ee"
    And I set the "Total_price" to "10.12"
    And I select "ACTIVE" in the "Status" dropdown
    And I press the "Update" button
    Then I should see the message "Success"
    When I press the "Clear" button
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see "5" in the "user_id" field
    And I should see "ee" in the "name" field
    And I should see "10.12" in the "Total_price" field
    And I should see "ACTIVE" in the "Status" dropdown

Scenario: Search for a Shopcart by Name
    When I visit the "Home Page"
    And I set the "Name" to "bb"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "bb" in the results
    And I should not see "aa" in the results
    And I should not see "cc" in the results
    And I should not see "dd" in the results

