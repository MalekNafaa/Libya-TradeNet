*** Settings ***
Library    SeleniumLibrary

*** Variables ***
${BASE_URL}     http://127.0.0.1:8000/en
${BROWSER}      chrome
${DELAY}        0.2s
${TEST_OTP}     123456

*** Keywords ***
Open Libya TradeNet
    Open Browser    ${BASE_URL}/login/    ${BROWSER}
    Maximize Browser Window
    Set Selenium Speed    ${DELAY}

Login As
    [Arguments]    ${username}    ${password}
    Input Text      name:username    ${username}
    Input Text      name:password    ${password}
    Click Button    xpath://button[@type='submit']

Login As With OTP
    [Arguments]    ${username}    ${password}
    Login As    ${username}    ${password}
    Wait Until Page Contains    verification code    timeout=5s
    Input Text      name:otp    ${TEST_OTP}
    Click Button    xpath://button[@type='submit']

Logout
    Go To    ${BASE_URL}/logout/

Close Test Browser
    Close Browser
