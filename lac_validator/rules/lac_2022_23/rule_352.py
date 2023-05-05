import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="352",
    message="Child who started to be looked after was aged 18 or over.",
    affected_fields=["DECOM", "RNE"],
)
def validate(dfs):
    if "Header" not in dfs:
        return {}
    if "Episodes" not in dfs:
        return {}
    else:
        header = dfs["Header"]
        episodes = dfs["Episodes"]

        header["DOB"] = pd.todatetime(header["DOB"], format="%d/%m/%Y", errors="coerce")
        episodes["DECOM"] = pd.todatetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        header["DOB18"] = header["DOB"] + pd.DateOffset(years=18)

        episodesmerged = (
            episodes.resetindex()
            .merge(
                header,
                how="left",
                on=["CHILD"],
                suffixes=("", "header"),
                indicator=True,
            )
            .setindex("index")
        )

        carestart = episodesmerged["RNE"].str.upper().astype(str).isin(["S"])
        startedover18 = episodesmerged["DOB18"] <= episodesmerged["DECOM"]

        errormask = carestart & startedover18

        errorlocations = episodesmerged.index[errormask].unique()

        return {"Episodes": errorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "CHILD": ["101", "102", "101", "102", "103"],
            "RNE": ["S", "S", "X1", pd.NA, "S"],
            "DECOM": ["16/03/2021", "17/06/2020", "20/03/2020", pd.NA, "23/08/2020"],
        }
    )

    fake_data_child = pd.DataFrame(
        {
            "CHILD": ["101", "102", "103", "103"],
            "DOB": ["16/03/2005", "23/09/2002", "31/12/2000", "31/12/2000"],
        }
    )

    fake_dfs = {"Episodes": fake_data, "Header": fake_data_child}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [4]}
