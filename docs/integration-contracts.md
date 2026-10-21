# Integration contracts

> [!IMPORTANT]
> **Every interface on this page is proposed.** There is no TypeScript in this repository and nothing implements these types. They exist so frontend, services and indexer can be built against agreed shapes. Change them here first, then in code.

## Contents

- [Conventions](#conventions)
- [Shared types](#shared-types)
- [Token](#token)
- [LaunchRequest](#launchrequest)
- [FeeAllocation](#feeallocation)
- [PurchaseRecord](#purchaserecord)
- [TreasurySnapshot](#treasurysnapshot)
- [ShieldVerification](#shieldverification)
- [CreatorLock](#creatorlock)
- [TransactionRecord](#transactionrecord)
- [JSON encoding](#json-encoding)
- [Versioning](#versioning)

## Conventions

| Rule | Reason |
| :-- | :-- |
| Amounts are `bigint` in TypeScript and decimal integer strings in JSON | No floating point money; JSON numbers lose precision above 2^53 |
| SOL amounts are lamports, token amounts are base units | One unit per field, named in the field |
| Addresses and signatures are base58 strings | Matches Solana tooling |
| Every chain derived value carries `slot` | Freshness and reproducibility |
| Times are ISO 8601 strings in UTC | Unambiguous |
| Enumerations are string unions | Readable in logs and JSON |

## Shared types

```ts
// PROPOSED
export type Base58Address = string;
export type Base58Signature = string;
export type Lamports = bigint;
export type BaseUnits = bigint;
export type Bps = bigint; // 0n..10_000n
export type Slot = bigint;
export type IsoTime = string;
export type Commitment = "processed" | "confirmed" | "finalized";
export type Cluster = "devnet" | "mainnet-beta" | "localnet";

export type VerificationState = "verified" | "pending" | "not_enabled" | "failed" | "unknown";

export interface ChainRef {
  slot: Slot;
  commitment: Commitment;
  readAt: IsoTime;
}
```

## Token

```ts
// PROPOSED
export interface Token {
  mint: Base58Address;
  tokenProgram: "spl-token" | "token-2022";
  name: string;
  symbol: string;
  decimals: number;
  totalSupply: BaseUnits;
  metadataUri: string;
  creator: Base58Address;
  quoteAsset: "SOL";          // launched tokens trade in SOL, never paired with TRUMP
  launchId: string;
  createdAt: ChainRef;
}
```

## LaunchRequest

The creator's draft, validated client side before any transaction is built.

```ts
// PROPOSED
export interface LaunchRequest {
  launchId: string;                 // stable for the life of the draft; idempotency key
  cluster: Cluster;
  creator: Base58Address;
  name: string;                     // length limits set by the metadata standard chosen
  symbol: string;
  decimals: number;                 // 0..9 proposed
  totalSupply: BaseUnits;
  image: { contentType: "image/png" | "image/jpeg" | "image/webp"; bytes: number };
  creatorAllocation: BaseUnits;     // amount intended for escrow; 0n if none
  lock: null | {
    startAt: IsoTime;
    cliffAt: IsoTime | null;
    endAt: IsoTime;
    releaseEverySeconds: number;
  };
  disclosedAllocationBps: Bps;      // TRUMP allocation shown to the creator at launch
  acknowledgedAt: IsoTime;          // creator confirmed the disclosures
}

export type LaunchValidationError =
  | { field: keyof LaunchRequest; code: "required" | "too_long" | "out_of_range" | "invalid_format" }
  | { field: "lock"; code: "end_before_start" | "cliff_outside_range" }
  | { field: "creatorAllocation"; code: "exceeds_supply" };
```

## FeeAllocation

One row per collection event.

```ts
// PROPOSED
export interface FeeAllocation {
  id: string;
  launchId: string;
  mint: Base58Address;
  collectionSignature: Base58Signature;
  collected: Lamports;              // F
  allocationBps: Bps;               // a_bps in force at the collection slot
  allocated: Lamports;              // A = floor(F * a_bps / 10_000)
  remainder: Lamports;              // F - A
  status: "collected" | "allocated" | "purchase_pending" | "purchased" | "reconciled";
  purchaseIds: string[];            // more than one if split across batches
  collectedAt: ChainRef;
}
```

Invariant: `allocated + remainder === collected`.

## PurchaseRecord

```ts
// PROPOSED
export interface PurchaseRecord {
  id: string;
  batchAllocationIds: string[];
  swapInput: Lamports;              // S
  executionCosts: Lamports;         // C, zero if the operator pays costs
  trumpMint: Base58Address;         // must equal the published TRUMP mint
  treasuryTokenAccount: Base58Address;
  quotedOut: BaseUnits;
  minOut: BaseUnits;
  slippageBps: Bps;
  status: "pending" | "submitted" | "confirmed" | "failed" | "mismatch" | "reconciled";
  transaction: TransactionRecord | null;
  received: BaseUnits | null;       // Q, set only by reconciliation
  attribution: { allocationId: string; share: BaseUnits }[]; // sums exactly to received
}
```

## TreasurySnapshot

```ts
// PROPOSED
export interface TreasurySnapshot {
  treasuryTokenAccount: Base58Address;
  trumpMint: Base58Address;
  trumpDecimals: number;            // read from the mint
  balance: BaseUnits;               // as read from chain
  reconciledReceived: BaseUnits;    // sum of reconciled Q
  unexplainedDifference: BaseUnits; // balance - reconciledReceived - known other flows
  allocatedNotPurchased: Lamports;
  at: ChainRef;
  indexerLagSlots: bigint;
}
```

`unexplainedDifference` should be zero. Anything else is surfaced publicly.

## ShieldVerification

```ts
// PROPOSED
export type ShieldCheck =
  | "token_program" | "mint_authority" | "freeze_authority" | "supply" | "decimals"
  | "token_extensions" | "metadata_uri" | "metadata_update_authority"
  | "escrow_program" | "escrow_deposit" | "escrow_schedule" | "escrow_recipient" | "escrow_cancellation"
  | "fee_allocation" | "fee_destination" | "fee_config_authority" | "fee_changeability";

export interface ShieldCheckResult {
  check: ShieldCheck;
  state: VerificationState;
  observed: string | null;
  expected: string | null;
  account: Base58Address;
  ownerProgram: Base58Address | null;
  warnings: string[];               // e.g. "transfer hook present: <program>"
  ref: ChainRef;
  rpcProviderLabel: string;         // a label, never a URL containing credentials
}

export interface ShieldVerification {
  launchId: string;
  mint: Base58Address;
  summary: VerificationState;       // see the aggregation rule in shield.md
  checks: ShieldCheckResult[];
  verifierVersion: string;
  freshUntil: IsoTime;              // after this, display as unknown and re-run
}
```

## CreatorLock

```ts
// PROPOSED
export interface CreatorLock {
  launchId: string;
  escrowProgram: Base58Address;
  escrowAccount: Base58Address;
  escrowTokenAccount: Base58Address;
  mint: Base58Address;
  recipient: Base58Address;
  deposited: BaseUnits;
  withdrawn: BaseUnits;
  schedule: { startAt: IsoTime; cliffAt: IsoTime | null; endAt: IsoTime; releaseEverySeconds: number };
  unlockedAtRead: BaseUnits;        // computed from schedule at ref.slot time
  cancelAuthority: Base58Address | null;
  programUpgradeAuthority: Base58Address | null;
  ref: ChainRef;
}
```

## TransactionRecord

The step journal entry used by the launch adapter and the purchase executor.

```ts
// PROPOSED
export type LaunchStep =
  | "create_mint" | "create_metadata" | "mint_supply" | "revoke_authorities"
  | "open_market" | "configure_fees" | "escrow_deposit" | "verify";

export interface TransactionRecord {
  id: string;
  launchId: string | null;          // null for purchase transactions
  step: LaunchStep | "collect_fees" | "swap";
  attempt: number;
  signature: Base58Signature | null; // recorded before send
  recentBlockhash: string | null;
  lastValidBlockHeight: bigint | null;
  status: "prepared" | "signed" | "submitted" | "confirmed" | "finalized" | "failed" | "expired";
  error: { kind: "user_rejected" | "simulation" | "program" | "rpc" | "expired"; message: string } | null;
  updatedAt: IsoTime;
  ref: ChainRef | null;
}
```

## JSON encoding

`bigint` does not serialize with `JSON.stringify`. On the wire every `bigint` field is a decimal string matching `^(0|[1-9][0-9]*)$`, and parsers reject anything else, including exponent notation and leading zeros.

```json
{
  "id": "alloc_01",
  "collected": "3250000000",
  "allocationBps": "2500",
  "allocated": "812500000",
  "remainder": "2437500000"
}
```

## Versioning

Contracts carry a version once code exists. Additive optional fields are minor changes. Renaming, removing or changing the unit of a field is a breaking change and requires a new version.
