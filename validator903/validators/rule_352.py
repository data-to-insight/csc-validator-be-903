import pandas as pd

from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="352",
        description="Child who started to be looked after was aged 18 or over.",
        affected_fields=["DECOM", "RNE"],
    )

    def _validate(dfs):
        if "Header" not in dfs:
            return {}
        if "Episodes" not in dfs:
            return {}
        else:
            header = dfs["Header"]
            episodes = dfs["Episodes"]

            header["DOB"] = pd.to_datetime(
                header["DOB"], format="%d/%m/%Y", errors="coerce"
            )
            episodes["DECOM"] = pd.to_datetime(
                episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
            )
            header["DOB18"] = header["DOB"] + pd.DateOffset(years=18)

            episodes_merged = (
                episodes.reset_index()
                .merge(
                    header,
                    how="left",
                    on=["CHILD"],
                    suffixes=("", "_header"),
                    indicator=True,
                )
                .set_index("index")
            )

            care_start = episodes_merged["RNE"].str.upper().astype(str).isin(["S"])
            started_over_18 = episodes_merged["DOB18"] <= episodes_merged["DECOM"]

            error_mask = care_start & started_over_18

            error_locations = episodes_merged.index[error_mask].unique()

            return {"Episodes": error_locations.to_list()}

    return error, _validate


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
