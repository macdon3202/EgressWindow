# EgressWindow V1 specification

## Proof obligation

For a case-bound authority, release tag, chain, object, operation and policy,
establish whether the official release notice explicitly offers an actionable
exit before an announced restriction takes effect and whether the notice period
meets the immutable policy minimum.

## Evidence boundary

The contract establishes what the fetched official notice says. It does not
observe protocol liquidity, contract pause state, transaction execution or user
behavior. `DISCLOSURE_CONFIRMED` is therefore a disclosure certificate, not an
availability or safety certificate.

## Judgment authority

Validators independently determine only:

- semantic object and exit/migration-function binding;
- whether a restriction is announced;
- whether exit remains available before it;
- whether instructions are explicit;
- whether material exceptions are stated;
- explicit, timezone-resolved effective/deadline timestamps.

## Execution authority

Deterministic contract code controls:

- source construction and authority/tag binding;
- fetched-content digest computation;
- policy/function consistency;
- observer independence;
- lifecycle and replay protection;
- timestamp ordering and minimum duration;
- final state derivation;
- append-only supersession.

## State derivation

`DISCLOSURE_CONFIRMED` requires every mandatory predicate to be positively
known. `UNKNOWN`, zero timestamps, mismatches, invalid source data and model
schema errors cannot reach the positive state.

Source failures are `UNRESOLVED`, not factual claims that a protocol failed to
provide an exit. Material exceptions are `REVIEW_REQUIRED`.

## Supersession

A new release tag may open a new case referencing a terminal prior case when
authority, chain, object and operation match. The prior record is never edited.
