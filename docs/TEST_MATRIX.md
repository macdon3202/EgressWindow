# Test matrix

| Invariant or branch | Expected result | Automated |
|---|---|---:|
| Explicit qualifying exit notice | `DISCLOSURE_CONFIRMED` | yes |
| Notice period below policy minimum | `INSUFFICIENT_WINDOW` | yes |
| Exit deadline too early but effective date much later | `INSUFFICIENT_WINDOW` | regression required |
| Exit deadline exactly at policy minimum | `DISCLOSURE_CONFIRMED` | boundary required |
| No actionable exit | `NO_ACTIONABLE_EXIT` | yes |
| Unknown timestamps | `UNRESOLVED` | yes |
| Material exception | `REVIEW_REQUIRED` | yes |
| Source unavailable | `UNRESOLVED` | yes |
| Wrong canonical repository URL | `BINDING_FAILED` | yes |
| Wrong returned tag | `BINDING_FAILED` | yes |
| Wrong object | `BINDING_FAILED` | yes |
| Creator attempts observation | revert + full no-mutation | yes |
| Terminal replay | revert + full no-mutation | yes |
| Superseding release | new append-only case | yes |
| Supersede nonterminal case | revert | yes |
| Duplicate case identity | revert | yes |
| Unknown authority | revert | yes |
| Policy/function mismatch | revert | yes |
| Malformed AI payload | `UNRESOLVED` | yes |
| Consensus failure | rollback + no observation | yes |
