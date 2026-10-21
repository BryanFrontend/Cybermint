# Contributing to Cybermint

Cybermint is in the documentation and design stage. This repository has no application code, so contributions today are limited to documentation, design decisions and artwork.

## Before you start

- Read the [README](README.md), in particular the [status labels](README.md#current-implementation-status).
- For anything larger than a typo, open an issue first describing the change and why.
- No license has been chosen for this repository. Until the maintainers choose one, it is unclear under what terms contributions would be used. Keep that in mind before investing significant work.

## What fits here

| Welcome | Not accepted yet |
| :-- | :-- |
| Corrections to technical facts about Solana, SPL Token or Token-2022 | Application, service or onchain program code without a prior design discussion |
| Clarifications of mechanisms, states and failure handling | Placeholder code, empty directories or stub services |
| Design proposals for open decisions, with trade-offs | Badges or claims for builds, coverage or audits that do not exist |
| Artwork changes made through `tools/artwork/` | Hand edits to outlined SVGs |

## Rules for every change

1. **Label status honestly.** Every capability is one of: implemented and verified, implemented but not verified, planned, or external integration required.
2. **No unsupported claims.** No audits, deployments, partnerships, adoption figures, performance numbers, security guarantees or endorsements without linkable evidence.
3. **Do not guess addresses.** The TRUMP mint, treasury address, escrow program ID and production domain are left blank until maintainers publish them.
4. **Integers for money.** Lamports for SOL, base units for tokens, basis points for fractions. Label illustrative values.
5. **House style.** No em dashes and no emojis.
6. **No secrets.** Never commit private keys, seed phrases, API keys or `.env` files.

## Checks

Run before opening a pull request:

```bash
node scripts/check-docs.mjs
```

If you changed artwork, regenerate it and look at the result at roughly 900 px wide (GitHub's README width) as well as full size:

```bash
python3 tools/artwork/build_assets.py docs/assets tools/artwork/logo-layers.json
```

See [docs/development.md](docs/development.md) for requirements.

## Pull requests

- Keep each pull request to one topic.
- Explain which open decision or document section it affects.
- If a change moves a capability between status labels, update the README matrix and the status strip artwork in the same pull request, and say what evidence supports the new label.

## Security issues

Do not open public issues with vulnerability details. Read [SECURITY.md](SECURITY.md) first.
