*** Settings ***
Library    SeleniumLibrary

*** Variables ***
${BASE_URL}     http://127.0.0.1:8000/en
${BROWSER}      chrome
${DELAY}        0.2s

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

Logout
    Go To    ${BASE_URL}/logout/

Close Test Browser
    Close Browser
