*** Settings ***
Library     SeleniumLibrary
Resource    resources/common.robot

*** Test Cases ***
Admin Dashboard Loads Successfully
    Open Libya TradeNet
    Login As With OTP    Malek    admin123
    Page Should Contain    Dashboard
    Page Should Contain Element    xpath://nav
    [Teardown]    Close Test Browser

Admin Can Navigate To Companies
    Open Libya TradeNet
    Login As With OTP    Malek    admin123
    Go To    ${BASE_URL}/gov/companies/
    Page Should Not Contain    500
    Page Should Not Contain    TemplateDoesNotExist
    [Teardown]    Close Test Browser

Admin Can Navigate To Licenses
    Open Libya TradeNet
    Login As With OTP    Malek    admin123
    Go To    ${BASE_URL}/gov/licenses/
    Page Should Not Contain    500
    [Teardown]    Close Test Browser

Admin Can Navigate To Import Permits
    Open Libya TradeNet
    Login As With OTP    Malek    admin123
    Go To    ${BASE_URL}/gov/import-permits/
    Page Should Not Contain    500
    [Teardown]    Close Test Browser

Unauthenticated User Redirected To Login
    Open Browser    ${BASE_URL}/gov/admin/    ${BROWSER}
    Location Should Contain    login
    [Teardown]    Close Test Browser
