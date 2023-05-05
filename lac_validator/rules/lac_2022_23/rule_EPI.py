import pandas as pd

from validator903.types import ErrorDefinition


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

        header["indexheader"] = header.index

        merged = header.merge(
            episodes["CHILD"],
            on="CHILD",
            indicator="mergeeps",
            how="left",
            suffixes=["", "episodes"],
        )

        merged = merged.merge(
            oc3["CHILD"],
            on="CHILD",
            indicator="mergeoc3",
            how="left",
            suffixes=["", "oc3"],
        )

        mask = (merged["mergeeps"] == "leftonly") & (merged["mergeoc3"] == "leftonly")
        epserrorlocations = merged.loc[mask, "indexheader"]
        return {"Header": epserrorlocations.unique().tolist()}


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
