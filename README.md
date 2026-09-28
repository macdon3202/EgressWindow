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

Current result: **17 tests passing**.

## Repository map

- `contracts/egress_window.py` — Intelligent Contract
- `tests/test_egress_window.py` — local, failure and adversarial tests
- `docs/SPECIFICATION.md` — proof obligation and state derivation
- `docs/TEST_RESOURCE_MANIFEST.md` — allowed live/synthetic evidence
- `docs/TEST_MATRIX.md` — required branch coverage
- `scripts/run_studionet_e2e.py` — two-wallet live evidence runner

V2 live evidence is retained as historical audit evidence. V3 has a finalized
positive migration lifecycle plus a separate finalized adversarial ledger.

## Studionet deployment

Current V3 contract:
[`0xF853b3a956a184f77A6ca60C0d5f3Fa106F714B5`](https://explorer-studio.genlayer.com/address/0xF853b3a956a184f77A6ca60C0d5f3Fa106F714B5)

Evidence: [`docs/studionet-v3-e2e.json`](docs/studionet-v3-e2e.json) and
[`docs/studionet-adversarial.json`](docs/studionet-adversarial.json).

Historical V1 config readback: `EGRESS_WINDOW_V1` with architecture
`AUTHORITY_BOUND_APPEND_ONLY_EXIT_CERTIFICATES`.

V1 correctly rolled back two observations when validators returned
`MAJORITY_DISAGREE`. V2 narrows comparative consensus to the exact deterministic
state/reason consequence while retaining exact source identity, content digest
and positive/interval timestamps. **The address above is historical V1 and V2
must be redeployed before positive lifecycle evidence is collected.**
