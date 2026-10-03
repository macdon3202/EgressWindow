"""Live role, replay, duplicate, and unavailable-source audit for V4."""
from __future__ import annotations
import json
import os
from pathlib import Path
import time
from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet
from run_studionet_e2e import RPC, load_wallets, read, send

def main():
    load_wallets()
    address = os.environ.get("EGRESS_WINDOW_ADDRESS", "")
    if not address:
        raise SystemExit("Set EGRESS_WINDOW_ADDRESS to the reviewed V4 deployment")
    author = create_account(os.environ["SERVICE_LEDGER_KEY_A"])
    observer = create_account(os.environ["SERVICE_LEDGER_KEY_B"])
    client = create_client(chain=studionet, account=author, endpoint=RPC)
    config = read(client, address, author, "get_config", [])
    if config.get("version") != "EGRESS_WINDOW_V4":
        raise RuntimeError(f"Refusing source/deployment mismatch: {config.get('version')}")
    proof = {"contract": address, "version": "EGRESS_WINDOW_V4", "transactions": [], "readbacks": {}}

    # Terminal replay must finalize as an error and preserve the complete case.
    before = read(client, address, observer, "get_case", [1])
    proof["transactions"].append(send(client, address, observer, "observe_case", [1], expect_error=True))
    after = read(client, address, observer, "get_case", [1])
    assert before == after
    proof["readbacks"]["terminal_replay_unchanged"] = after

    # Duplicate identity must not increment the case counter.
    count_before = read(client, address, author, "get_config", [])["case_count"]
    proof["transactions"].append(send(client, address, observer, "register_case", ["OPTIMISM", "op-reth/v2.4.1", "OP_MAINNET", "HISTORICAL_PROOFS_V1_DB", "MIGRATE", "MIGRATE_7D", 0], expect_error=True))
    count_after = read(client, address, author, "get_config", [])["case_count"]
    assert count_before == count_after
    proof["readbacks"]["duplicate_count_unchanged"] = count_after

    # A unique, validly-shaped case proves the creator cannot perform its own
    # observation. Dynamic IDs make this runner safe to resume after a partial
    # network run without silently assuming the next case number.
    nonce = int(time.time())
    self_tag = f"egress-window-self-observe-{nonce}"
    proof["transactions"].append(send(client, address, author, "register_case", ["OPTIMISM", self_tag, "OP_MAINNET", "OP_PROPOSER", "MIGRATE", "MIGRATE_7D", 0]))
    self_case_id = int(read(client, address, author, "get_config", [])["case_count"])
    self_case = read(client, address, author, "get_case", [self_case_id])
    proof["transactions"].append(send(client, address, author, "observe_case", [self_case_id], expect_error=True))
    assert read(client, address, author, "get_case", [self_case_id]) == self_case
    proof["readbacks"]["self_observation_unchanged"] = self_case

    # A validly-shaped but nonexistent official tag becomes UNRESOLVED, not a
    # negative factual accusation.
    missing_tag = f"egress-window-nonexistent-{nonce}"
    proof["transactions"].append(send(client, address, author, "register_case", ["OPTIMISM", missing_tag, "OP_MAINNET", "OP_PROPOSER", "MIGRATE", "MIGRATE_7D", 0]))
    missing_case_id = int(read(client, address, author, "get_config", [])["case_count"])
    proof["transactions"].append(send(client, address, observer, "observe_case", [missing_case_id]))
    missing = read(client, address, observer, "get_case", [missing_case_id])
    assert missing["state"] == "UNRESOLVED" and missing["reason"] == "SOURCE_INVALID"
    proof["readbacks"]["missing_source"] = missing
    proof["result"] = "PASS"
    out = Path(__file__).resolve().parents[1] / "docs" / "studionet-adversarial.json"
    out.write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(proof, indent=2))


if __name__ == "__main__":
    main()
