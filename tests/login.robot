*** Settings ***
Library     SeleniumLibrary
Resource    resources/common.robot

*** Test Cases ***
Valid Government Login With OTP
    Open Libya TradeNet
    Login As With OTP    Malek    Test1234
    Location Should Contain    gov/admin
    [Teardown]    Close Test Browser

Invalid Login Shows Error Message
    Open Libya TradeNet
    Login As    wronguser    wrongpass
    Location Should Contain    login
    Page Should Contain Element    xpath://div[contains(@class,'alert') or contains(@class,'error') or contains(@class,'messages')]
    [Teardown]    Close Test Browser

Empty Login Shows Validation Error
    Open Libya TradeNet
    Click Button    xpath://button[@type='submit']
    Page Should Not Contain    Dashboard
    [Teardown]    Close Test Browser

Company Owner Login Without OTP
    Open Libya TradeNet
    Login As    ali.alfituri_1    testpass
    Page Should Not Contain    verification code
    [Teardown]    Close Test Browser
