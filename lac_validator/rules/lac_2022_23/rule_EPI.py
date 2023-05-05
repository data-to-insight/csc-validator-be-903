import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="EPI",
    message="WARNING: Episodes need to be loaded for this child before further validation is possible "
    "[NOTE: This refers to the DfE portal - here, all checks that can be performed with only the "
    "available data will be.]",
    affected_fields=["CHILD"],
)
def validate(dfs):
    if "Header" not in dfs:
        return {}
    else:
        header = dfs["Header"]

        if "Episodes" not in dfs:
            episodes = pd.DataFrame(columns=["CHILD"])
        else:
            episodes = dfs["Episodes"]

        if "OC3" not in dfs:
            oc3 = pd.DataFrame(columns=["CHILD"])
        else:
            oc3 = dfs["OC3"]

        header["index_header"] = header.index

        merged = header.merge(
            episodes["CHILD"],
            on="CHILD",
            indicator="_merge_eps",
            how="left",
            suffixes=["", "_episodes"],
        )

        merged = merged.merge(
            oc3["CHILD"],
            on="CHILD",
            indicator="_merge_oc3",
            how="left",
            suffixes=["", "_oc3"],
        )

        mask = (merged["_merge_eps"] == "left_only") & (
            merged["_merge_oc3"] == "left_only"
        )
        eps_error_locations = merged.loc[mask, "index_header"]
        return {"Header": eps_error_locations.unique().tolist()}


def test_validate():
    import pandas as pd

    fake_header = pd.DataFrame(
        {
            "CHILD": ["101", "102", "103", "106"],
        }
    )

    fake_episodes = pd.DataFrame(
        {
            "CHILD": ["101", "101", "103"],
        }
    )

    erro_defn, error_func = validate()

    fake_dfs = {"Header": fake_header, "Episodes": fake_episodes}
    result = error_func(fake_dfs)
    assert result == {"Header": [1, 3]}


# Testing rule with Header, Episodes and OC3 provided.
