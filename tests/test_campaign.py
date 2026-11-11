"""Tests of the tasks, the scoring and the LLM arms, on the copied data."""

import json

import numpy as np
import pytest

from wsp import MLPHead, dump_weights, zero_
from wsp.arms import (
    EDIT_HIDDEN,
    affine_recalibration,
    edit_prompt,
    edit_setup,
    gp_with_prior,
    score_edit,
    score_write,
    write_prompt,
)
from wsp.baselines import predict, prepare, score
from wsp.edit import EditError
from wsp.serialize import WeightTextError
from wsp.tasks import DATA, TASK_NAMES, load_task

pytestmark = pytest.mark.skipif(
    not (DATA / "PROVENANCE.md").exists(), reason="run scripts/copy_from_siblings.py first"
)


@pytest.mark.parametrize("name", TASK_NAMES)
def test_task_is_finite_and_its_split_is_disjoint(name):
    task = load_task(name)
    assert task.X.shape == (len(task.y), len(task.feature_names))
    assert np.isfinite(task.X).all() and np.isfinite(task.y).all()
    train, test = task.split(0)
    assert len(train) > 0 and len(test) > 0
    assert not set(train) & set(test)


def test_closed_loop_split_never_mixes_runs():
    """Each run has its own PCA basis; a seed must stay inside one run."""
    task = load_task("loop_bulk_modulus")
    train0, test0 = task.split(0)
    train1, test1 = task.split(1)
    assert not set(train0) & set(train1)
    assert not set(test0) & set(test1)
    assert len(train0) == 500  # the warm-start pool
    # same structures, same labels, different coordinates
    assert np.allclose(np.sort(task.y[train0]), np.sort(task.y[train1]))
    assert not np.allclose(task.X[train0], task.X[train1])


def test_composition_rows_sum_to_one():
    for name in ("mpea_yield_strength", "ti_alloy_youngs_modulus"):
        task = load_task(name)
        assert task.named_features
        assert np.allclose(task.X.sum(axis=1), 1.0)


def test_score_reports_underprediction_of_the_top_tenth_as_negative():
    y = np.arange(100.0)
    shrunk = 50 + 0.5 * (y - 50)
    assert score(y, shrunk)["top_decile_bias"] < 0
    assert score(y, y)["top_decile_bias"] == 0
    assert score(y, y)["r2"] == 1


def test_edit_prompt_states_the_fault_and_carries_the_weights():
    prompt = edit_prompt(load_task("ti_alloy_youngs_modulus"), seed=0)
    assert "decile of true value" in prompt
    assert "## net.4.weight shape=(1, 32)" in prompt
    assert "JSON list of edits" in prompt


def test_an_output_stretch_keeps_the_ranking_and_counts_33_weights():
    task = load_task("ti_alloy_youngs_modulus")
    data, head, _ = edit_setup(task, 0)
    weight = head.state_dict()["net.4.weight"][0]
    edits = [{"tensor": "net.4.weight", "index": [0, i], "value": float(1.1 * w)} for i, w in enumerate(weight)]
    edits.append({"tensor": "net.4.bias", "index": [0], "value": float(1.1 * head.state_dict()["net.4.bias"][0])})
    result = score_edit(task, 0, json.dumps(edits))
    assert result["weights_changed"] == 33
    # float32 rounding of the rescaled outputs can swap near-tied predictions
    assert result["llm_edit"]["spearman"] == pytest.approx(result["unedited"]["spearman"], abs=1e-3)


def test_a_malformed_edit_reply_scores_nothing():
    with pytest.raises(EditError):
        score_edit(load_task("ti_alloy_youngs_modulus"), 0, '[{"tensor": "net.9.weight", "index": [0], "value": 1}]')


def test_shuffled_control_keeps_each_tensors_values():
    task = load_task("ti_alloy_youngs_modulus")
    _, head, _ = edit_setup(task, 0)
    _, shuffled, _ = edit_setup(task, 0, shuffled=True)
    for name, tensor in head.state_dict().items():
        other = shuffled.state_dict()[name]
        assert np.allclose(np.sort(tensor.flatten().numpy()), np.sort(other.flatten().numpy()))
    assert not np.allclose(head.state_dict()["net.0.weight"].numpy(), shuffled.state_dict()["net.0.weight"].numpy())


def test_affine_recalibration_is_the_identity_for_perfect_predictions():
    data = prepare(load_task("ti_alloy_youngs_modulus"), 0)
    assert np.allclose(affine_recalibration(data, data.y_train, data.y_test), data.y_test)


def test_write_prompt_names_every_input_and_needs_named_features():
    task = load_task("ti_alloy_youngs_modulus")
    prompt = write_prompt(task)
    assert all(name in prompt for name in task.feature_names)
    with pytest.raises(ValueError):
        write_prompt(load_task("loop_bulk_modulus"))


def test_a_useless_written_prior_reduces_to_a_plain_gp():
    data = prepare(load_task("ti_alloy_youngs_modulus"), 0)
    mean, std, slope = gp_with_prior(data, np.zeros(len(data.y_train)), np.zeros(len(data.y_test)))
    assert slope == 0
    assert np.isfinite(mean).all() and (std > 0).all()


def test_score_write_rejects_a_reply_of_the_wrong_shape():
    task = load_task("ti_alloy_youngs_modulus")
    wrong = dump_weights(zero_(MLPHead(task.X.shape[1], EDIT_HIDDEN, 1)).state_dict())
    with pytest.raises((RuntimeError, WeightTextError)):
        score_write(task, wrong, seeds=1, sizes=(10,))


def test_predict_returns_physical_units():
    task = load_task("ti_alloy_youngs_modulus")
    data, head, _ = edit_setup(task, 0)
    prediction = predict(head, data.U_test)
    assert 20 < prediction.mean() < 200  # GPa, not standardised units
