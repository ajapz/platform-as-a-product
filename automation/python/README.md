# Platform Automation

Python CLI for platform guardrails and reliability checks.

## Setup

- `python -m pip install -e .[dev]`

## Commands

- `platformctl validate-manifests <path>`
- `platformctl generate-baseline-netpol <namespace> --output <file>`
- `platformctl generate-netpol-bundle --namespaces-file <file> --output-dir <dir>`
- `platformctl generate-netpol-bundle --namespace <ns1> --namespace <ns2> --output-dir <dir>`
- `platformctl check-ha <path>`

CI uses `generate-netpol-bundle` to detect drift between namespace manifests and committed baseline network policy bundles.

## Run tests

- `pytest -q`
