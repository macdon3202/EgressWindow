"""Two-wallet Studionet E2E runner for EgressWindow.

Set EGRESS_WINDOW_ADDRESS and the fixture variables below only after selecting
an existing release from an allowed official repository. The script refuses to
run with placeholders so synthetic evidence cannot be mistaken for a live run.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import time
from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet

RPC = "https://studio.genlayer.com/api"
EXPLORER = "https://explorer-studio.genlayer.com"


def load_wallets() -> None:
    path = Path(__file__).resolve().parents[2] / "secrets" / "genlayer-test-wallets.env"
    for raw in path.read_text(encoding="utf-8").splitlines():
        if "=" in raw and not raw.lstrip().startswith("#"):
            key, value = raw.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("'\"").strip("<>"))


def plain(value):
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(v) for v in value]
    return value if isinstance(value, (str, int, float, bool)) or value is None else str(value)


def read(client, address, account, method, args):
    last_error = None
    for attempt in range(8):
        try:
            return plain(client.read_contract(address=address, function_name=method, args=args, account=account))
        except Exception as error:
            last_error = error
            if attempt < 7:
                time.sleep(2 + attempt)
    raise last_error


def signals(info):
    status = str(info.get("status_name") or info.get("status") or "UNKNOWN").upper()
    consensus = str(info.get("result_name") or info.get("consensus_result_name") or info.get("consensus_result") or "UNKNOWN").upper()
    receipts = []
    data = info.get("consensus_data")
    if isinstance(data, dict):
        receipts = data.get("leader_receipt") or data.get("validators") or []
    if isinstance(receipts, dict):
        receipts = [receipts]
    leader = next((r for r in receipts if isinstance(r, dict) and str(r.get("mode", "")).lower() == "leader"), None)
    execution = str((leader or {}).get("execution_result") or info.get("execution_result") or "UNKNOWN").upper()
    return status, consensus, execution


def send(client, address, account, method, args, expect_error=False):
    tx = str(client.write_contract(address=address, function_name=method, account=account, args=args, value=0))
    print(json.dumps({"submitted": method, "tx": tx}), flush=True)
    for _ in range(200):
        info = plain(client.get_transaction(tx))
        status, consensus, execution = signals(info)
        if status == "FINALIZED":
            success = consensus in {"MAJORITY_AGREE", "AGREE", "ACCEPTED"} and execution == "SUCCESS"
            if expect_error == success:
                raise AssertionError(f"{method}: expect_error={expect_error}, consensus={consensus}, execution={execution}, tx={tx}")
            return {"method": method, "tx": tx, "explorer": f"{EXPLORER}/tx/{tx}", "status": status, "consensus": consensus, "execution": execution}
        time.sleep(3)
    raise TimeoutError(tx)


def main() -> None:
    load_wallets()
    address = os.environ.get("EGRESS_WINDOW_ADDRESS", "")
    tag = os.environ.get("EGRESS_WINDOW_RELEASE_TAG", "")
    object_key = os.environ.get("EGRESS_WINDOW_OBJECT", "")
    affected_function = os.environ.get("EGRESS_WINDOW_FUNCTION", "")
    policy_id = os.environ.get("EGRESS_WINDOW_POLICY", "")
    chain_key = os.environ.get("EGRESS_WINDOW_CHAIN", "OP_MAINNET")
    if not address or not tag or not object_key or not affected_function or not policy_id:
        raise SystemExit("Set address, release tag, object, function and policy only after fixture review")
    author = create_account(os.environ["SERVICE_LEDGER_KEY_A"])
    observer = create_account(os.environ["SERVICE_LEDGER_KEY_B"])
    client = create_client(chain=studionet, account=author, endpoint=RPC)
    before = read(client, address, author, "get_config", [])
    create = send(client, address, author, "register_case", ["OPTIMISM", tag, chain_key, object_key, affected_function, policy_id, 0])
    case_id = int(read(client, address, author, "get_config", [])["case_count"])
    registered = read(client, address, author, "get_case", [case_id])
    observation = send(client, address, observer, "observe_case", [case_id])
    final = read(client, address, observer, "get_case", [case_id])
    evidence = {"contract": address, "fixture": {"authority": "OPTIMISM", "release_tag": tag, "chain_key": chain_key, "object_key": object_key, "affected_function": affected_function, "policy_id": policy_id}, "before": before, "case_id": case_id, "transactions": [create, observation], "registered": registered, "final": final}
    print(json.dumps(evidence, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
