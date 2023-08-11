import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="302",
    message="First episode starts before child was born.",
    affected_fields=["DECOM", "DOB"],
)
def validate(dfs):
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

        episodes = episodes.reset_index()
        header = header.reset_index()

        episodes = episodes.loc[episodes.groupby("CHILD")["DECOM"].idxmin()]

        merged = episodes.merge(
            header, how="left", on=["CHILD"], suffixes=("_eps", "_hdr")
        )

        # omitting looking for the 'S' episode as we may not have it in current year's data
        # care_start = merged['RNE'].str.upper().astype(str).isin(['S'])

        started_before_born = merged["DOB"] > merged["DECOM"]

        eps_errors = merged.loc[started_before_born, "index_eps"].to_list()
        hdr_errors = merged.loc[started_before_born, "index_hdr"].to_list()
        return {"Episodes": eps_errors, "Header": hdr_errors}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "CHILD": ["101", "102", "101", "102", "103", "104", "104"],
            "RNE": ["S", "S", "X1", pd.NA, "S", "X", "X"],
            "DECOM": [
                "16/03/2021",
                "17/06/2020",
                "20/03/2020",
                pd.NA,
                "23/08/2020",
                "01/02/1988",
                "03/04/1994",
            ],
        }
    )

    fake_data_child = pd.DataFrame(
        {
            "CHILD": ["101", "102", "103", "104"],
            "DOB": ["16/03/2021", "23/09/2019", "31/12/2020", "01/01/1995"],
        }
    )

    fake_dfs = {"Episodes": fake_data, "Header": fake_data_child}

    result = validate(fake_dfs)

    assert result == {"Episodes": [2, 4, 5], "Header": [0, 2, 3]}
