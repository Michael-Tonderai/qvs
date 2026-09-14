# QVS Qualification Verification System

QVS is a web-based system for registering, searching and verifying academic and professional qualifications while maintaining an auditable history of verification activities.

## What It Does

- Registers qualifications and professional certifications.
- Searches for records using a certificate ID, holder name or institution.
- Verifies whether a qualification is authentic and has not been altered.
- Maintains a permanent, append-only history of every verification attempt.

Each qualification is issued with a unique, non-guessable certificate ID and an HMAC-SHA256 signature. When a certificate is checked, the system returns VERIFIED, NOT FOUND or TAMPERED.

## Try It

The live system is available at:

https://qvs-f3dk.onrender.com/verify/

Use the following demonstration certificate ID:

QVS-TEST-CASE-2345-6789

The first visit may take up to a minute while the free Render server wakes up. Anyone can verify a qualification without an account. Registering qualifications and searching for records require an authorised user account.

## Built With

- Python and Django for the web application.
- SQLite for database storage.
- pytest for automated unit and integration tests.
- GitHub Actions for the CI/CD pipeline.
- Docker for containerisation.
- Render for public deployment over HTTPS.

The pipeline automatically runs tests, code quality checks, security scans,and the Docker build.

## How the Code Is Organised

- main is the protected release branch.
- develop is the branch where completed work is integrated.
- Each change is developed on a separate feature or fix branch.
- Changes are submitted through pull requests.
- Required CI checks must pass before changes can reach main.

This workflow provides evidence of collaboration through commits, branches, pull requests, code reviews, issue tracking and pipeline executions.

## Where to Read More

- docs/REQUIREMENTS.md contains the requirements register, requirement IDs and verification mechanisms.
- docs/DECISIONS.md explains the architectural and technological decisions.
- docs/report contains the technical report and supporting evidence.
