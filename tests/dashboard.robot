*** Settings ***
Library     SeleniumLibrary
Resource    resources/common.robot

*** Test Cases ***
Admin Dashboard Loads Successfully
    Open Libya TradeNet
    Login As With OTP    Malek    Test1234
    Location Should Contain    gov/admin
    Page Should Contain Element    xpath://nav
    [Teardown]    Close Test Browser

Admin Can Navigate To Companies
    Open Libya TradeNet
    Login As With OTP    Malek    Test1234
    Go To    ${BASE_URL}/gov/companies/
    Page Should Not Contain    Internal Server Error
    Page Should Not Contain    TemplateDoesNotExist
    [Teardown]    Close Test Browser

Admin Can Navigate To Licenses
    Open Libya TradeNet
    Login As With OTP    Malek    Test1234
    Go To    ${BASE_URL}/gov/licenses/
    Page Should Not Contain    Internal Server Error
    [Teardown]    Close Test Browser

Admin Can Navigate To Import Permits
    Open Libya TradeNet
    Login As With OTP    Malek    Test1234
    Go To    ${BASE_URL}/imports/
    Page Should Not Contain    Internal Server Error
    [Teardown]    Close Test Browser

Unauthenticated User Redirected To Login
    Open Browser    ${BASE_URL}/gov/admin/    ${BROWSER}
    Location Should Contain    login
    [Teardown]    Close Test Browser
