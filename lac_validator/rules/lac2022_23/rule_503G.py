import pandas as pd

from lac_validator.fixtures import current_episodes, previous_episodes
from lac_validator.rule_engine import rule_definition
from lac_validator.rules.rule_utils import compare_placement_coordinates


@rule_definition(
    code="503G",
    message="The distance in first episode does not match open episode at end of last year.",
    affected_fields=["PL_DISTANCE"],
)
def validate(dfs):
    return compare_placement_coordinates(dfs, field="PL_DISTANCE")
 

def test_validate():
    fake_epi = current_episodes.copy()
    fake_epi_last = previous_episodes.copy()

    fake_epi["DECOM"] = pd.to_datetime(
        fake_epi["DECOM"], format="%d/%m/%Y", errors="coerce"
    )
    fake_epi_last["DECOM"] = pd.to_datetime(
        fake_epi_last["DECOM"], format="%d/%m/%Y", errors="coerce"
    )
    fake_epi_last["DEC"] = pd.to_datetime(
        fake_epi_last["DEC"], format="%d/%m/%Y", errors="coerce"
    )

    fake_dfs = {"Episodes": fake_epi, "Episodes_last": fake_epi_last}

    result = validate(fake_dfs)

    assert result == {"Episodes": [4]}
