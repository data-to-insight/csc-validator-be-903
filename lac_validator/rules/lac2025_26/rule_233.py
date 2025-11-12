import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="233",
    message="Reason for placement change is not required when the episode has not ceased.",
    affected_fields=["REASON_PLACE_CHANGE", "REASON_PLACE_CHANGE"],
    tables=["Episodes"],
)
def validate(dfs):
    # If DATE_EPISODE_CEASED is null then <REASON_PLACE_CHANGE> should be null
    if "Episodes" not in dfs:
        return {}

    episodes = dfs["Episodes"]

    failure_rows = (episodes["DATE_EPISODE_CEASED"].isna()) & (
        episodes["REASON_PLACE_CHANGE"].notna()
    )

    validation_error_locations = episodes.index[failure_rows]

    return {"Episodes": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "DATE_EPISODE_CEASED": ["data", pd.NA, pd.NA, "data"],
            "REASON_PLACE_CHANGE": [pd.NA, pd.NA, "data", "data"],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"Episodes": [2]}
