import pandas as pd

from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="NoE",
    message="This child has no episodes loaded for previous year even though child started to be looked after before this current year.",
    affected_fields=["DECOM"],
)
def validate(dfs):
    if "Episodes" not in dfs or "Episodes_last" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        episodes["DECOM"] = pd.to_datetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        episodes_last = dfs["Episodes_last"]
        episodes_last["DECOM"] = pd.to_datetime(
            episodes_last["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        collection_start = pd.to_datetime(
            dfs["metadata"]["collection_start"], format="%d/%m/%Y", errors="coerce"
        )

        episodes_before_year = episodes[episodes["DECOM"] < collection_start]

        episodes_merged = (
            episodes_before_year.reset_index()
            .merge(episodes_last, how="left", on=["CHILD"], indicator=True)
            .set_index("index")
        )

        episodes_not_matched = episodes_merged[episodes_merged["_merge"] == "left_only"]

        error_mask = episodes.index.isin(episodes_not_matched.index)

        error_locations = episodes.index[error_mask]

        return {"Episodes": error_locations.to_list()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "CHILD": ["101", "102", "103"],
            "DECOM": ["14/03/2021", "08/09/2021", "03/10/2020"],
        }
    )

    fake_data_prev = pd.DataFrame(
        {"CHILD": ["101", "102"], "DECOM": ["14/03/2021", "16/06/2019"]}
    )

    metadata = {"collection_start": "01/04/2021"}

    fake_dfs = {
        "Episodes": fake_data,
        "Episodes_last": fake_data_prev,
        "metadata": metadata,
    }

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [2]}
