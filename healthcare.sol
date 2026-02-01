// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract HealthcareDataAccess {

    address public healthcareProvider;
    address public patient;
    address public authorizedParty;
    bool public consentGiven;

    event AccessGranted(address indexed healthcareProvider, address indexed authorizedParty, bool granted);

    modifier onlyPatient() {
        require(msg.sender == patient, "Only the patient can grant or revoke consent.");
        _;
    }

    modifier onlyHealthcareProvider() {
        require(msg.sender == healthcareProvider, "Only healthcare provider can request access.");
        _;
    }

    constructor(address _patient, address _healthcareProvider) {
        healthcareProvider = _healthcareProvider;
        patient = _patient;
        consentGiven = false;
    }

    function grantOrRevokeConsent(bool _consent) public onlyPatient {
        consentGiven = _consent;
        emit AccessGranted(healthcareProvider, authorizedParty, consentGiven);
    }

    function requestDataAccess(address _authorizedParty) public onlyHealthcareProvider {
        authorizedParty = _authorizedParty;
        require(consentGiven == true, "Patient has not granted consent.");
        emit AccessGranted(healthcareProvider, authorizedParty, true);
    }

    function denyAccess() public onlyHealthcareProvider {
        emit AccessGranted(healthcareProvider, authorizedParty, false);
    }
}
