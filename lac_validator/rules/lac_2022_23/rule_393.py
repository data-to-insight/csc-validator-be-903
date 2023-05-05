from validator903.types import ErrorDefinition


@rule_definition(
    code="393",
    message="Child is looked after but mother field is not completed.",
    affected_fields=["MOTHER"],
)
def validate(dfs):
    if "Header" not in dfs or "Episodes" not in dfs:
        return {}
    else:
        header = dfs["Header"]
        episodes = dfs["Episodes"]

        headerfemale = header[header["SEX"].astype(str) == "2"]

        applicableepisodes = episodes[~episodes["LS"].str.upper().isin(["V3", "V4"])]

        errormask = (
            headerfemale["CHILD"].isin(applicableepisodes["CHILD"])
            & headerfemale["MOTHER"].isna()
        )

        errorlocations = headerfemale.index[errormask]

        return {"Header": errorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "CHILD": ["101", "102", "103", "104", "105"],
            "SEX": ["2", "1", "2", "2", "2"],
            "MOTHER": ["1", pd.NA, "0", pd.NA, pd.NA],
        }
    )

    fake_data_episodes = pd.DataFrame(
        {
            "CHILD": ["101", "102", "103", "104", "105"],
            "LS": ["C2", "C2", "c2", "C1", "v4"],
        }
    )

    fake_dfs = {"Header": fake_data, "Episodes": fake_data_episodes}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Header": [3]}
