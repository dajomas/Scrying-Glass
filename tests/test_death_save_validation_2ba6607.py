"""Regression coverage for death-save input validation before transitions."""
import copy
import pytest
import test_encounter_features as feature_tests
from test_sqlite_storage import HTTPError

@pytest.fixture
def encounter():
    fixture = feature_tests.FeatureTests(methodName='test_death_saves')
    fixture.setUp()
    fixture.call('edit_features', 'c', {'life_state': 'down'})
    yield fixture
    fixture.tearDown()

@pytest.mark.parametrize('body', [
    {'death_successes': 3.0},
    {'death_successes': 3, 'death_failures': 4},
    {'death_successes': 3, 'death_failures': -1},
    {'death_successes': 3, 'death_failures': True},
    {'death_successes': 3, 'death_failures': None},
    {'death_successes': 3, 'death_failures': '2'},
    {'life_state': 'stable', 'death_successes': True},
    {'life_state': 'stable', 'death_failures': 4},
])
def test_invalid_counters_rejected_without_side_effects(encounter, body):
    c = encounter.c
    before = copy.deepcopy(c.STATE)
    database_before = list(c.STORAGE.connection.iterdump())
    with pytest.raises(HTTPError) as raised:
        encounter.call('edit_features', 'c', body)
    assert raised.value.status_code == 422
    assert c.STATE == before
    assert list(c.STORAGE.connection.iterdump()) == database_before

@pytest.mark.parametrize('field', ['death_successes', 'death_failures'])
@pytest.mark.parametrize('value', [True, False, None, '1', 1.0, [], {}, -1, 4])
def test_counter_contract(encounter, field, value):
    with pytest.raises(HTTPError) as raised:
        encounter.call('edit_features', 'c', {field: value})
    assert raised.value.status_code == 422

@pytest.mark.parametrize('body,state', [
    ({'death_successes': 2, 'death_failures': 1}, 'down'),
    ({'death_successes': 3, 'death_failures': 2}, 'stable'),
    ({'death_successes': 2, 'death_failures': 3}, 'dead'),
    ({'death_successes': 3, 'death_failures': 3}, 'dead'),
])
def test_valid_integer_transitions_preserved(encounter, body, state):
    encounter.call('edit_features', 'c', body)
    assert encounter.item('c')['life_state'] == state

@pytest.mark.parametrize('body', [{'death_successes': 3.0}, {'death_failures': True}])
def test_raw_validation_precedes_target_normalization(encounter, body):
    from unittest.mock import patch
    with patch.object(encounter.f, 'target', side_effect=AssertionError('target accessed')):
        with pytest.raises(HTTPError) as raised:
            encounter.call('edit_features', 'c', body)
    assert raised.value.status_code == 422
