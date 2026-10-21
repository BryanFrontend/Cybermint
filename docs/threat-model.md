# Threat model

> [!IMPORTANT]
> This threat model covers the **proposed** system. Because no code exists, every control below is **planned**, and none has been implemented or tested. It should be revisited at each roadmap milestone and before any external review.

## Contents

- [Scope](#scope)
- [Assets](#assets)
- [Actors](#actors)
- [Trust boundaries](#trust-boundaries)
- [Threats and planned controls](#threats-and-planned-controls)
- [Residual risks](#residual-risks)
- [Review triggers](#review-triggers)

## Scope

In scope: the launch flow, the fee collection and purchase pipeline, the public treasury, Shield verification, and the services and keys they require. Out of scope: Solana consensus, wallet software internals, and the internal security of external programs beyond how Cybermint selects and displays them.

## Assets

| Asset | Why it matters |
| :-- | :-- |
| Creator keys | Control the creator's funds and launch authorities. Never held by Cybermint. |
| Purchase signer key | Spends allocated SOL. Highest value server key. |
| Fee collection authority | Moves collected fees, if the fee source design requires one. |
| Treasury authority | Controls acquired TRUMP. |
| Program upgrade authorities | Can change behavior of any Cybermint program, if one is deployed. |
| Configuration (`a_bps`, TRUMP mint, treasury address) | Wrong values redirect or misreport funds. |
| Ledger and reconciliation data | Basis of public claims about TRUMP purchased. |
| Shield results | Users rely on them to judge launches. |
| Metadata storage credentials | Could replace or remove token images and metadata. |

## Actors

| Actor | Capability |
| :-- | :-- |
| Honest creator | Signs their launch, may misconfigure it |
| Malicious creator | Wants to look safer than they are; may hold tokens through other wallets |
| Trader | Reads Shield and treasury data; may be misled by stale or optimistic data |
| External attacker | Phishing, dependency compromise, server compromise, RPC manipulation |
| Malicious or compromised operator | Has access to server keys and configuration |
| Compromised dependency | Malicious package in the frontend or services |
| Faulty or malicious RPC | Returns stale or false data |
| Searcher or MEV bot | Front runs or sandwiches purchase swaps |

## Trust boundaries

1. **Browser to wallet.** The creator trusts the wallet to show what they sign.
2. **Browser to server.** The server is trusted to store metadata faithfully and report verification honestly; the browser should verify independently where possible.
3. **Server to chain.** Server signers act within narrowly scoped authority.
4. **Anything to RPC.** RPC answers are trusted for correctness and freshness, mitigated by recording slots and cross checking.
5. **Cybermint to external programs.** Escrow, swap and token programs are trusted to behave as reviewed.

## Threats and planned controls

| ID | Threat | Impact | Planned control | Status |
| :-- | :-- | :-- | :-- | :-- |
| T1 | Phishing clone of the launch site asks users to sign malicious transactions | Loss of user funds | Publish canonical domain once chosen; transaction summaries; simulation before signing | Planned |
| T2 | Compromised frontend dependency alters transactions | Loss of creator funds | Lockfile, dependency review, minimal dependencies, subresource integrity where applicable, simulation check of expected account changes | Planned |
| T3 | Purchase signer key theft | Allocated SOL stolen | Custody in a key management system or multisig; signer can only call the swap route with the treasury as output; spend limits | Planned, custody undecided |
| T4 | Purchase output redirected to a wrong account or wrong mint | TRUMP not delivered to treasury | Executor hard checks output mint and treasury account against published values; reconciliation flags mismatch | Planned |
| T5 | Operator changes `a_bps` silently | Disclosure becomes false | Configuration change authority and history visible; Shield fee checks; changes apply to future collections only | Planned |
| T6 | Treasury drained by its authority | Public treasury claim becomes false | Treasury custody published; preference for an authority that cannot withdraw, or a multisig with public membership | Undecided |
| T7 | Escrow program has cancel or admin withdraw path | Creator lock is weaker than shown | Shield reads and displays cancel and admin authorities; never reports such a lock as unconditional | Planned |
| T8 | Upgradeable program changes behavior after review | Any guarantee derived from it lapses | Display upgrade authority; re-review on upgrade; alert on program data changes | Planned |
| T9 | RPC returns stale or false data | Wrong Shield results, wrong totals | Record slot; require `finalized` for Verified; cross check critical reads against a second provider; stale results become Unknown | Planned |
| T10 | Indexer lag shows zero purchases | Public misreporting | Report lag; lagging data shown as Pending | Planned |
| T11 | Optimistic UI shows unconfirmed launch as live | Users trade a partial launch | UI distinguishes confirmed from finalized; partial launches labelled | Planned |
| T12 | Expired transaction rebuilt too early, both land | Duplicate actions | Expiry proven by block height and absent signature before rebuild | Planned |
| T13 | Duplicate launch request | Two mints for one draft | `launchId` idempotency, fixed mint address per draft | Planned |
| T14 | Malicious Token-2022 extension configuration | Holders can be frozen, taxed or drained | Shield enumerates extensions and fails permanent delegate, pausable, non-transferable and default frozen state | Planned |
| T15 | Swap sandwiched or executed at poor price | Lower `Q` | Minimum output from quote and slippage limit; batching to reduce frequency; route selection | Planned |
| T16 | Metadata replaced after launch | Misleading token page | Show metadata mutability and update authority; content addressed storage preferred | Planned |
| T17 | Secrets leaked through browser bundle | Credential theft | Browser safe configuration only; secret-like names rejected in `.env.example` by the docs check | Partly in place: the docs check exists; no bundle exists |
| T18 | Marketing implies guarantees Shield cannot give | Users over trust launches | Copy rules in CONTRIBUTING; "cannot establish" list shown next to every summary | Planned |
| T19 | Sensitive vulnerability report posted publicly | Exploit before fix | Private reporting channel must be enabled first; see SECURITY.md | Not configured |

## Residual risks

These remain even if every planned control works:

- creators can hold and sell tokens through undisclosed wallets
- market losses, including total loss, are always possible
- external programs and venues can fail or change
- a compromised wallet or device can make a user sign anything
- operator honesty still matters wherever custody is not enforced by a program

## Review triggers

Update this document when any of the following happens: a market venue, escrow program or swap route is selected; a Cybermint program is written; a server signer is introduced; treasury custody is decided; the first deployment to any cluster; any security report.
