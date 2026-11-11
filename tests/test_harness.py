import pytest
import torch

from wsp import (
    EditError,
    MLPHead,
    WeightTextError,
    apply_edits,
    build_prompt,
    count_weights,
    diff,
    dump_weights,
    load_weights,
    parse_edits,
    round_trip_error,
    zero_,
)


def test_round_trip_keeps_names_shapes_and_values_to_the_rounding():
    torch.manual_seed(0)
    head = MLPHead(50, [32, 32], 1)
    state = head.state_dict()
    restored = load_weights(dump_weights(state, decimals=4))
    assert list(restored) == list(state)
    for name, tensor in state.items():
        assert restored[name].shape == tensor.shape
    assert round_trip_error(state, decimals=4) <= 0.5e-4 + 1e-9


def test_count_weights_matches_the_formula():
    assert count_weights(MLPHead(50, [32, 32], 1).state_dict()) == 50 * 32 + 32 + 32 * 32 + 32 + 32 + 1


def test_weights_written_by_hand_as_text_compute_the_intended_function():
    """|a - b| = relu(a - b) + relu(b - a): a network written with no gradient step."""
    text = """
    ## net.0.weight shape=(2, 2)
    1 -1
    -1 1
    ## net.0.bias shape=(2,)
    0 0
    ## net.2.weight shape=(1, 2)
    1 1
    ## net.2.bias shape=(1,)
    0
    """
    head = zero_(MLPHead(2, [2], 1))
    head.load_state_dict(load_weights(text))
    x = torch.tensor([[3.0, 1.0], [1.0, 3.0], [-2.0, 5.0], [4.0, 4.0]])
    assert torch.allclose(head(x).squeeze(1), torch.tensor([2.0, 2.0, 7.0, 0.0]))


def test_three_dimensional_tensor_round_trips():
    state = {"conv.weight": torch.arange(24, dtype=torch.float32).reshape(2, 3, 4) / 8}
    assert torch.equal(load_weights(dump_weights(state))["conv.weight"], state["conv.weight"])


@pytest.mark.parametrize(
    "text",
    [
        "1 2 3\n",  # numbers before a header
        "## w shape=(2, 2)\n1 2 3\n",  # too few numbers
        "## w shape=(1,)\nabc\n",  # not a number
        "## w shape=(1,)\nnan\n",  # non-finite
        "## w shape=(1,)\n1\n## w shape=(1,)\n2\n",  # duplicate tensor
        "",  # nothing
    ],
)
def test_malformed_text_is_rejected(text):
    with pytest.raises(WeightTextError):
        load_weights(text)


def test_edits_apply_to_a_copy_and_the_diff_counts_them():
    state = zero_(MLPHead(4, [3], 1)).state_dict()
    edits = parse_edits(
        '[{"tensor": "net.0.weight", "index": [2, 1], "value": 0.5},'
        ' {"tensor": "net.2.bias", "index": [0], "value": -1}]'
    )
    edited = apply_edits(state, edits)
    assert state["net.0.weight"][2, 1] == 0  # input untouched
    assert edited["net.0.weight"][2, 1] == 0.5
    report = diff(state, edited)
    assert report.changed == 2
    assert report.total == count_weights(state)
    assert report.max_abs_change == 1.0
    assert report.changed_by_tensor == {"net.0.weight": 1, "net.2.bias": 1}


@pytest.mark.parametrize(
    "edits",
    [
        '[{"tensor": "nope", "index": [0], "value": 1}]',
        '[{"tensor": "net.0.weight", "index": [9, 0], "value": 1}]',
        '[{"tensor": "net.0.weight", "index": [0], "value": 1}]',
        '[{"tensor": "net.0.weight", "index": [0, 0]}]',
        '{"tensor": "net.0.weight"}',
        "not json",
    ],
)
def test_bad_edits_are_rejected_and_change_nothing(edits):
    state = zero_(MLPHead(4, [3], 1)).state_dict()
    with pytest.raises(EditError):
        apply_edits(state, parse_edits(edits))
    assert all((t == 0).all() for t in state.values())


def test_prompt_carries_task_architecture_weights_and_reply_format():
    head = zero_(MLPHead(2, [2], 1))
    prompt = build_prompt("edit", "Make y = |x0 - x1|.", head.describe(), head.state_dict())
    assert "Make y = |x0 - x1|." in prompt
    assert "h1 = relu(net.0.weight @ h0 + net.0.bias)" in prompt
    assert "y = net.2.weight @ h1 + net.2.bias" in prompt
    assert "## net.0.weight shape=(2, 2)" in prompt
    assert "JSON list of edits" in prompt
    with pytest.raises(ValueError):
        build_prompt("train", "x", "y", head.state_dict())
