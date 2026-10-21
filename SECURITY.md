# Security

## Current state

This repository contains documentation, artwork, a documentation check script and an artwork generator. It contains no application, service, smart contract or deployment, and it does not handle funds or keys.

No security audit has been performed. No component has been reviewed by a third party.

## Reporting

**A private vulnerability reporting channel has not been configured yet.**

Before inviting sensitive reports, the maintainers need to enable one, for example GitHub private vulnerability reporting in the repository's security settings, and then update this file with how to use it.

Until that is done:

- Do not post vulnerability details, exploit code or affected addresses in public issues, pull requests or discussions.
- If you believe you have found something sensitive, open a public issue that says only that you need a private contact, with no technical detail.

There is no bug bounty program, and no response time is promised.

## Scope

Today, relevant reports would concern:

- secrets accidentally committed to the repository
- SVG or Markdown content that could execute code or load remote resources when rendered
- documentation that would lead an implementer to build something unsafe (for example, an incorrect description of authority checks)

Reports about a Cybermint website, token or program are out of scope for this repository, because none is published from it. Treat any site or token claiming to be the Cybermint launchpad with caution until the maintainers publish canonical addresses and a domain.

## For future implementers

The planned controls and residual risks are in [docs/threat-model.md](docs/threat-model.md). Before any mainnet deployment, the roadmap requires an independent review of any program, the signer custody model and the threat model.
