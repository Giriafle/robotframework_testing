*** Settings ***
Library           library/DBRequests.py
Library           library/Api.py
Test Setup        Get Connection And Cursor DB
Test Teardown     DBRequests.Close Db    ${db_connection}

*** Test Cases ***
Check File DB
    [Tags]    db    smoke
    ${result} =    DBRequests.Check File
    Convert To Boolean    ${result}
    Should Be True    ${result}

Check Connection to API
    [Tags]    api    smoke
    Api.Check Connection

Add Services To Users With Positive Balance
    [Documentation]    Test adds services to user with positive balance or create such user and add it to him
    [Tags]    db    api
    ${client_id}     ${client_balance} =    DBRequests.Get Client With Positive Balance    ${db_cursor}
    Run Keyword If    ${client_id} == None    Insert User    ${db_connection}    ${db_cursor}
    ${hooked_services} =    Api.Get Hook Services    ${client_id}
    ${all_services} =    Api.Get All Services
    ${service_id}    ${service_cost} =    Api.Find Unhooked Service    ${hooked_services}    ${all_services}
    Api.Add Services    ${client_id}    ${service_id}
    Wait Until Keyword Succeeds    1 min    1 sec    Wait For Adding    ${client_id}    ${service_id}
    ${new_balance_from_db} =    DBRequests.Get Balance    ${client_id}    ${db_cursor}
    ${calculated_balance} =    Evaluate     ${client_balance} - ${service_cost}
    Should Be Equal    ${new_balance_from_db}    ${calculated_balance}    New client's balance from the database is not equal client's calculated balance

*** Keywords ***
Get Connection And Cursor DB
    ${db_connection} =    DBRequests.Open Connection
    ${db_cursor} =    DBRequests.Get Cursor    ${db_connection}
    Set Test Variable    ${db_connection}
    Set Test Variable    ${db_cursor}

Wait For Adding
    [Arguments]    ${client_id}    ${service_id}
    ${response} =    Api.Find Service In Hook Services    ${client_id}    ${service_id}
    Convert To Boolean    ${response}
    Should Be True    ${response}

Insert User
    [Arguments]    ${db_connection}    ${db_cursor}
    Log To Console    The client with positive balance is not found. Trying to insert it to the database.
    ${client_id}     ${client_balance} =    DBRequests.Insert User With Positive Balance    ${db_connection}    ${db_cursor}
    Set Test Variable    ${client_id}
    Set Test Variable    ${client_balance}

