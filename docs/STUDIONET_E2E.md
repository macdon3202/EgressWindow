# Studionet E2E evidence

Status: **V3 LIVE HAPPY PATH AND ADVERSARIAL AUDIT PASS**.

## V3 live evidence

- Contract: [`0xF853b3a956a184f77A6ca60C0d5f3Fa106F714B5`](https://explorer-studio.genlayer.com/address/0xF853b3a956a184f77A6ca60C0d5f3Fa106F714B5)
- Version readback: `EGRESS_WINDOW_V3`
- Register: [`0x830394…a5a7`](https://explorer-studio.genlayer.com/tx/0x830394ac67a67801c0a12b90db393c999ebce5a0894a1222baaa1565d5e1a5a7) — finalized / majority agree / success.
- Observe: [`0xfad55f…4d3b`](https://explorer-studio.genlayer.com/tx/0xfad55f1744e09fd34f512eb90c827adc333af5aed1afba72da029d5dbf6f4d3b) — finalized / majority agree / success.
- Final readback: `DISCLOSURE_CONFIRMED / POLICY_WINDOW_SATISFIED`.
- Creator: `0xFeD97e2aE1A8C1983b7cA206B3545e6A2c685E43`.
- Independent observer: `0xc67532aeF9D2879cBA9375a02E6217A3524657B8`.
- Exact happy-path ledger: [`studionet-v3-e2e.json`](studionet-v3-e2e.json).
- Exact V3 adversarial ledger: [`studionet-adversarial.json`](studionet-adversarial.json).

The V3 adversarial run proves terminal replay and duplicate registration fail
with consensus-agreed execution errors, creator self-observation fails without
state mutation, and a nonexistent official tag resolves fail-closed as
`UNRESOLVED / SOURCE_INVALID`.

## V2 verified lifecycle and adversarial evidence

- Contract: [`0x1BA6C9e3560Cd6A98C1C16f42464C299aa03605A`](https://explorer-studio.genlayer.com/address/0x1BA6C9e3560Cd6A98C1C16f42464C299aa03605A)
- Register case 1: [`0x88e761…8350`](https://explorer-studio.genlayer.com/tx/0x88e76185d98ba884168c244a76fdc662c01eba0ed684a03da362f68b08f28350)
- Observe case 1: [`0xa59e72…ee0a`](https://explorer-studio.genlayer.com/tx/0xa59e723290280cf055e2d1d11900884808c7d606093023283a0f97232027ee0a)
- Final state: `BINDING_FAILED / NOTICE_BINDING_FAILED` (correctly fail-closed because a database migration notice is not an asset withdrawal notice).
- Full adversarial ledger and exact readbacks: [`studionet-adversarial.json`](studionet-adversarial.json).

The adversarial ledger proves terminal replay rejection, duplicate identity
rejection, independent-observer enforcement, unchanged state after rejected
writes, and `UNRESOLVED / SOURCE_INVALID` for a nonexistent official tag.

V3 adds the source-aligned `MIGRATE_7D` proof obligation and validates it against
the real `op-reth/v2.4.1` official release.

## V1 historical diagnosis

- Contract: [`0xeAB42Ec2a2ab86d40D90c9D5cF89e8109A0aeFed`](https://explorer-studio.genlayer.com/address/0xeAB42Ec2a2ab86d40D90c9D5cF89e8109A0aeFed)
- Version readback: `EGRESS_WINDOW_V1`
- Architecture readback: `AUTHORITY_BOUND_APPEND_ONLY_EXIT_CERTIFICATES`
- Contract source SHA-256: `654CEC8B2BFA351FB45C96C4F604C96783E022E5620844251771984C157672D8`
- Initial `case_count`: `0`

## V1 live transactions

| Action | Transaction | Consensus / execution | Readback |
|---|---|---|---|
| Register case 1 | [`0xca5dad…dbdd9`](https://explorer-studio.genlayer.com/tx/0xca5dadc6179bb7d7cead12ac212395f877cfb9455ee5c81d4c26f063d57dbdd9) | finalized majority agree / success | `REGISTERED` |
| Observe attempt 1 | [`0x9520cd…caa2c`](https://explorer-studio.genlayer.com/tx/0x9520cd32441427793107d96f0f0afbb658653c131a9b931d737e79f4261caa2c) | finalized majority disagree / leader success | complete state unchanged |
| Observe attempt 2 | [`0x96a0ab…add1d`](https://explorer-studio.genlayer.com/tx/0x96a0abb15af61f9fdd418d91cf1854a079bdfb2bb37eb203b1d119336bdadd1d) | finalized majority disagree / leader success | complete state unchanged |

Fixture: official `ethereum-optimism/optimism` release
`op-reth/v2.4.1`, object `HISTORICAL_PROOFS_V1_DB`, requested operation
`WITHDRAW`. The release discusses database/command deprecation rather than an
asset withdrawal. No positive outcome was expected or claimed.

The two disagreements exposed that V1 compared every semantic subfield even
when validators reached an equivalent non-positive consequence. V2 changes the
effect-aligned equivalence boundary; V1 is not submission-ready and must not be
presented as a completed successful lifecycle.

Transaction rows will be added only after finalized consensus, leader execution
and exact post-write readbacks have been verified. No synthetic local fixture is
represented as live evidence.
