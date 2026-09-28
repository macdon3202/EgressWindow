import json
from pathlib import Path
import pytest

CONTRACT = Path(__file__).parents[1] / "contracts" / "egress_window.py"
CREATOR = bytes.fromhex("11" * 20)
OBSERVER = bytes.fromhex("22" * 20)
THIRD = bytes.fromhex("33" * 20)
TAG = "egress-test-v1"
PUBLISHED = "2026-10-01T00:00:00Z"
PUBLISHED_TS = 1790812800
EFFECTIVE_TS = 1791590400
DEADLINE_TS = 1791417600


def deploy(vm, direct_deploy):
    vm.strict_mocks = True
    vm.check_pickling = True
    vm.warp("2026-09-28T12:00:00+00:00")
    with vm.prank(CREATOR):
        return direct_deploy(CONTRACT, sdk_version="v0.2.16")


def release(tag=TAG, body="Vault Alpha withdrawals remain available until 2026-10-08 UTC. Withdrawals are disabled when migration activates on 2026-10-10 UTC.", **change):
    value = {
        "id": 9001,
        "tag_name": tag,
        "html_url": f"https://github.com/ethereum-optimism/optimism/releases/tag/{tag}",
        "published_at": PUBLISHED,
        "body": body,
    }
    value.update(change)
    return value


def finding(**change):
    value = {
        "object_binding": "MATCH",
        "restriction_announced": "YES",
        "exit_available": "YES",
        "function_binding": "MATCH",
        "instruction_clarity": "EXPLICIT",
        "exceptions_present": "NO",
        "effective_at": EFFECTIVE_TS,
        "exit_deadline": DEADLINE_TS,
    }
    value.update(change)
    return value


def mocks(vm, payload=None, answer=None, status=200):
    vm.mock_web(r"api\.github\.com/repos/ethereum-optimism/optimism/releases/tags/", {"method": "GET", "status": status, "body": json.dumps(release() if payload is None else payload)})
    if status == 200 and isinstance(payload if payload is not None else release(), dict):
        vm.mock_llm("EGRESS_WINDOW_NOTICE_EXTRACTOR_V1", finding() if answer is None else answer)


def register(contract, vm, tag=TAG, supersedes=0, creator=CREATOR):
    with vm.prank(creator):
        return contract.register_case("OPTIMISM", tag, "OP_MAINNET", "VAULT_ALPHA", "WITHDRAW", "WITHDRAW_7D", supersedes)


def observe(contract, vm, **kwargs):
    mocks(vm, **kwargs)
    with vm.prank(OBSERVER):
        return contract.observe_case(1)


def test_explicit_policy_compliant_window_is_confirmed(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    assert register(contract, direct_vm) == 1
    assert observe(contract, direct_vm) == "DISCLOSURE_CONFIRMED"
    case = contract.get_case(1)
    observation = contract.get_observation(1)
    assert case["reason"] == "POLICY_WINDOW_SATISFIED"
    assert case["published_at"] == PUBLISHED_TS
    assert case["observer"].lower().endswith("22" * 20)
    assert len(case["content_digest"]) == 64
    assert observation["derived_state"] == "DISCLOSURE_CONFIRMED"


def test_cutover_date_may_equal_migration_deadline(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    register(contract, direct_vm)
    cutover = PUBLISHED_TS + 8 * 86400
    assert observe(contract, direct_vm, answer=finding(effective_at=cutover, exit_deadline=cutover)) == "DISCLOSURE_CONFIRMED"


def test_short_notice_window_is_deterministically_rejected(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    register(contract, direct_vm)
    assert observe(contract, direct_vm, answer=finding(effective_at=PUBLISHED_TS + 2 * 86400, exit_deadline=PUBLISHED_TS + 86400)) == "INSUFFICIENT_WINDOW"
    assert contract.get_case(1)["reason"] == "NOTICE_WINDOW_TOO_SHORT"


def test_no_exit_is_not_fabricated_into_breach(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    register(contract, direct_vm)
    assert observe(contract, direct_vm, answer=finding(exit_available="NO", instruction_clarity="AMBIGUOUS", exit_deadline=0)) == "NO_ACTIONABLE_EXIT"


def test_unknown_timestamp_fails_unresolved(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    register(contract, direct_vm)
    assert observe(contract, direct_vm, answer=finding(effective_at=0, exit_deadline=0)) == "UNRESOLVED"
    assert contract.get_case(1)["reason"] == "MANDATORY_FACT_UNKNOWN"


def test_material_exception_requires_review(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    register(contract, direct_vm)
    assert observe(contract, direct_vm, answer=finding(exceptions_present="YES")) == "REVIEW_REQUIRED"


def test_source_unavailable_fails_closed(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    register(contract, direct_vm)
    assert observe(contract, direct_vm, status=503) == "UNRESOLVED"
    assert contract.get_observation(1)["source_status"] == "UNAVAILABLE"


@pytest.mark.parametrize("change", [
    {"html_url": "https://github.com/attacker/optimism/releases/tag/egress-test-v1"},
    {"tag_name": "other-tag"},
])
def test_authority_or_tag_binding_mismatch(change, direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    register(contract, direct_vm)
    assert observe(contract, direct_vm, payload=release(**change)) == "BINDING_FAILED"


def test_object_mismatch_fails_binding(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    register(contract, direct_vm)
    assert observe(contract, direct_vm, answer=finding(object_binding="MISMATCH")) == "BINDING_FAILED"


def test_creator_cannot_observe_and_state_is_unchanged(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    register(contract, direct_vm)
    before = contract.get_case(1)
    with direct_vm.prank(CREATOR), direct_vm.expect_revert("INDEPENDENT_OBSERVER_REQUIRED"):
        contract.observe_case(1)
    assert contract.get_case(1) == before
    with direct_vm.expect_revert("OBSERVATION_NOT_FOUND"):
        contract.get_observation(1)


def test_terminal_replay_rejected_without_mutation(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    register(contract, direct_vm)
    observe(contract, direct_vm)
    before = contract.get_case(1)
    with direct_vm.prank(THIRD), direct_vm.expect_revert("CASE_TERMINAL"):
        contract.observe_case(1)
    assert contract.get_case(1) == before


def test_superseding_revision_is_append_only(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    register(contract, direct_vm)
    observe(contract, direct_vm)
    first = contract.get_case(1)
    with direct_vm.prank(THIRD):
        second_id = contract.register_case("OPTIMISM", "egress-test-v2", "OP_MAINNET", "VAULT_ALPHA", "WITHDRAW", "WITHDRAW_7D", 1)
    assert second_id == 2
    assert contract.get_case(2)["supersedes"] == 1
    assert contract.get_case(1) == first


def test_invalid_supersede_and_duplicate_are_rejected(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    register(contract, direct_vm)
    with direct_vm.prank(THIRD), direct_vm.expect_revert("PRIOR_CASE_NOT_TERMINAL"):
        contract.register_case("OPTIMISM", "egress-test-v2", "OP_MAINNET", "VAULT_ALPHA", "WITHDRAW", "WITHDRAW_7D", 1)
    with direct_vm.prank(THIRD), direct_vm.expect_revert("CASE_ALREADY_REGISTERED"):
        contract.register_case("OPTIMISM", TAG, "OP_MAINNET", "VAULT_ALPHA", "WITHDRAW", "WITHDRAW_7D", 0)


def test_policy_and_authority_are_closed_catalogs(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    with direct_vm.prank(CREATOR), direct_vm.expect_revert("AUTHORITY_NOT_ALLOWED"):
        contract.register_case("ATTACKER", TAG, "OP_MAINNET", "VAULT_ALPHA", "WITHDRAW", "WITHDRAW_7D", 0)
    with direct_vm.prank(CREATOR), direct_vm.expect_revert("POLICY_FUNCTION_MISMATCH"):
        contract.register_case("OPTIMISM", TAG, "OP_MAINNET", "VAULT_ALPHA", "REDEEM", "WITHDRAW_7D", 0)


def test_malformed_model_output_fails_closed(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    register(contract, direct_vm)
    assert observe(contract, direct_vm, answer={"verdict": "DISCLOSURE_CONFIRMED"}) == "UNRESOLVED"
    assert contract.get_case(1)["reason"] == "SOURCE_INVALID"


def test_consensus_failure_rolls_back(direct_vm, direct_deploy, monkeypatch):
    contract = deploy(direct_vm, direct_deploy)
    register(contract, direct_vm)
    before = contract.get_case(1)
    from genlayer import gl
    def disagree(*args, **kwargs):
        raise RuntimeError("validator consensus undetermined")
    monkeypatch.setattr(gl.eq_principle, "prompt_comparative", disagree)
    with direct_vm.prank(OBSERVER), pytest.raises(RuntimeError, match="consensus undetermined"):
        contract.observe_case(1)
    assert contract.get_case(1) == before
    with direct_vm.expect_revert("OBSERVATION_NOT_FOUND"):
        contract.get_observation(1)


def test_config_declares_distinct_architecture(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    config = contract.get_config()
    assert config["version"] == "EGRESS_WINDOW_V3"
    assert config["architecture"] == "AUTHORITY_BOUND_APPEND_ONLY_EXIT_CERTIFICATES"
    assert "MIGRATE_7D" in config["policies"]
