# EgressWindow

EgressWindow is a contract-only GenLayer application that issues a narrow,
append-only certificate about an official protocol notice:

> Did the notice explicitly provide a policy-compliant exit or migration
> window for the bound object before a restrictive change takes effect?

It does **not** claim that an exit transaction will succeed, liquidity exists,
the protocol is safe, or users actually withdrew.

## Why GenLayer

Release notices are unstructured prose. Validators must independently decide
whether the notice binds the requested object/function, announces a restriction,
contains actionable exit/migration instructions, defines timezone-resolved deadlines, and
states material exceptions. Deterministic contract code then enforces authority,
tag, policy, lifecycle, role-separation and interval invariants.

## Architecture

```text
closed authority + policy catalogs
             ↓
permissionless case registration
             ↓
independent official-release observation
             ↓
bounded semantic timeline extraction
             ↓
deterministic duration and safety gate
             ↓
append-only certificate / superseding case
```

This is not a pairwise document comparator. A case binds one official release,
one object, one operation and one immutable policy. A later release creates a
new case that references—but never overwrites—the prior certificate.

## Fixed authorities

- `OPTIMISM` → `ethereum-optimism/optimism`
- `ARBITRUM` → `OffchainLabs/nitro`
- `AAVE_V3` → `aave/aave-v3-core`

Users provide a release tag only. The contract constructs the GitHub API route
and verifies the returned canonical GitHub release URL and tag.

## Fixed policies

- `WITHDRAW_72H`
- `WITHDRAW_7D`
- `REDEEM_7D`
- `MIGRATE_7D`

## Local verification

```bash
python -m pytest -q
python -X utf8 -m genvm_linter.cli check contracts/egress_window.py
```

Current result: **20 tests passing**.

## Repository map

- `contracts/egress_window.py` — Intelligent Contract
- `tests/test_egress_window.py` — local, failure and adversarial tests
- `docs/SPECIFICATION.md` — proof obligation and state derivation
- `docs/TEST_RESOURCE_MANIFEST.md` — allowed live/synthetic evidence
- `docs/TEST_MATRIX.md` — required branch coverage
- `scripts/run_studionet_e2e.py` — two-wallet live evidence runner

Prior live evidence is retained as historical audit evidence. V4 has a
finalized two-wallet migration lifecycle plus a separate finalized adversarial
ledger, and its deployed version readback matches the submitted source.

## Studionet deployment

Current V4 contract:
[`0x3F03Ee9076dEB9AFA57EE077c8FE77542D38D9C0`](https://explorer-studio.genlayer.com/address/0x3F03Ee9076dEB9AFA57EE077c8FE77542D38D9C0)

Evidence: [`docs/studionet-v4-e2e.json`](docs/studionet-v4-e2e.json),
[`docs/studionet-v4-adversarial.json`](docs/studionet-v4-adversarial.json), and
the human-readable [`docs/STUDIONET_E2E.md`](docs/STUDIONET_E2E.md).

Reviewer entry point: [`REVIEW_RESPONSE.md`](REVIEW_RESPONSE.md). Deployment
transaction: [`0xb0f67a…c97c`](https://explorer-studio.genlayer.com/tx/0xb0f67af002e18bedde07eb041dbaba04af2e74b842e84f241bd7c9eadbe2c97c).

V4 measures the policy minimum against the actual actionable interval
`exit_deadline - published_at`. A later `effective_at` cannot rescue an exit
deadline that closed too early. Timestamp ordering still requires
`published_at < exit_deadline <= effective_at`.
