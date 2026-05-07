*** Settings ***
Library     SeleniumLibrary
Resource    resources/common.robot

*** Test Cases ***
Valid Login Redirects To Dashboard
    Open Libya TradeNet
    Login As    admin    admin
    Page Should Contain    Dashboard
    [Teardown]    Close Test Browser

Invalid Login Shows Error Message
    Open Libya TradeNet
    Login As    wronguser    wrongpass
    Page Should Contain    Please enter a correct username
    [Teardown]    Close Test Browser

Empty Login Shows Validation Error
    Open Libya TradeNet
    Click Button    xpath://button[@type='submit']
    Page Should Contain    This field is required
    [Teardown]    Close Test Browser
