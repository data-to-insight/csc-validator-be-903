import pandas as pd

from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="389",
    message="Reason episode ceased is that child transferred to care of adult social care services, but child is aged under 16.",
    affected_fields=["REC"],
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
        episodes["DEC"] = pd.to_datetime(
            episodes["DEC"], format="%d/%m/%Y", errors="coerce"
        )
        header["DOB16"] = header["DOB"] + pd.DateOffset(years=16)

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

        ceased_asc = episodes_merged["REC"].str.upper().astype(str).isin(["E7"])
        ceased_over_16 = episodes_merged["DOB16"] <= episodes_merged["DEC"]

        error_mask = ceased_asc & ~ceased_over_16

        error_locations = episodes_merged.index[error_mask].unique()

        return {"Episodes": error_locations.to_list()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "CHILD": ["101", "102", "101", "102", "103"],
            "REC": ["E7", "E7", "X1", pd.NA, "E7"],
            "DEC": ["16/03/2021", "17/06/2020", "20/03/2020", pd.NA, "23/08/2020"],
        }
    )

    fake_data_child = pd.DataFrame(
        {
            "CHILD": ["101", "102", "103", "103"],
            "DOB": ["16/03/2005", "23/09/2002", "31/12/2014", "31/12/2014"],
        }
    )

    fake_dfs = {"Episodes": fake_data, "Header": fake_data_child}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [4]}
