# EgressWindow V4 — reviewer response

This is the single entry point for reviewing the requested correction.

## What changed

The minimum notice window is now calculated from publication to the actual
exit deadline:

```python
exit_deadline - published_at
```

It is no longer calculated from publication to the later restriction-effective
date. The ordering invariant remains
`published_at < exit_deadline <= effective_at`.

## Matching submitted and deployed source

- [V4 deployed contract](https://explorer-studio.genlayer.com/address/0x3F03Ee9076dEB9AFA57EE077c8FE77542D38D9C0) — open its **Contract** tab to inspect `EGRESS_WINDOW_V4` and the corrected expression.
- [Deployment transaction](https://explorer-studio.genlayer.com/tx/0xb0f67af002e18bedde07eb041dbaba04af2e74b842e84f241bd7c9eadbe2c97c)
- [Submitted contract source](contracts/egress_window.py)
- Source SHA-256: `E9BD17C6C3D0419FEBE61E067503C7FD2D3D4ACC1581E47906394B595B423329`

## Requested regression

The deterministic regression fixes publication at day 0, exit deadline at day
1, and effective date at day 30. It proves the later effective date cannot
rescue the early deadline: the result is
`INSUFFICIENT_WINDOW / NOTICE_WINDOW_TOO_SHORT`.

- [Regression and boundary tests](tests/test_egress_window.py)
- [Test matrix](docs/TEST_MATRIX.md)
- Full suite: **20 passing tests**

The exact contradictory timestamp fixture is intentionally local/deterministic;
it is not misrepresented as a real official release.

## Live V4 evidence

- [Human-readable E2E report](docs/STUDIONET_E2E.md)
- [Two-wallet happy-path ledger](docs/studionet-v4-e2e.json)
- [Adversarial ledger](docs/studionet-v4-adversarial.json)
- [Register transaction](https://explorer-studio.genlayer.com/tx/0x841bc9bb76d0e03db4216269092c4ff331a04a8c72960df17ccbd050bc142dd0)
- [Independent observe transaction](https://explorer-studio.genlayer.com/tx/0x92c46a8504481b7e4795efe1d4b8eda1af2186372695f9a3ea9329f664bfc4a2)

The live happy path uses two distinct wallets and ends at
`DISCLOSURE_CONFIRMED / POLICY_WINDOW_SATISFIED`. The adversarial run proves
terminal replay, duplicate identity and creator self-observation fail without
mutating the protected state, while an invalid source fails closed.
