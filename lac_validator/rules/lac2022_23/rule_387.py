import pandas as pd

from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="387",
    message="Reason episode ceased is child moved into independent living arrangement, but the child is aged under 14.",
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
        header["DOB14"] = header["DOB"] + pd.DateOffset(years=14)

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

        ceased_indep = episodes_merged["REC"].str.upper().astype(str).isin(["E5", "E6"])
        ceased_over_14 = episodes_merged["DOB14"] <= episodes_merged["DEC"]
        dec_present = episodes_merged["DEC"].notna()

        error_mask = ceased_indep & ~ceased_over_14 & dec_present

        error_locations = episodes_merged.index[error_mask].unique()

        return {"Episodes": error_locations.to_list()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "CHILD": ["101", "102", "101", "102", "103", "104", "105"],
            "REC": ["E5", "E6", "X1", pd.NA, "E6", "E5", "E6"],
            "DEC": [
                "16/03/2021",
                "17/06/2020",
                "20/03/2020",
                pd.NA,
                "23/08/2020",
                "19XX/33rd",
                pd.NA,
            ],
        }
    )

    fake_data_child = pd.DataFrame(
        {
            "CHILD": ["101", "102", "103", "104", "105", "105"],
            "DOB": [
                "16/03/2005",
                "23/09/2002",
                "31/12/2014",
                "31/12/2014",
                "01/01/2004",
                "01/01/2004",
            ],
        }
    )

    fake_metadata = {"collection_end": "31/03/2021"}

    fake_dfs = {
        "Episodes": fake_data,
        "Header": fake_data_child,
        "metadata": fake_metadata,
    }

    

    result = validate(fake_dfs)

    assert result == {"Episodes": [4]}


# -------------------------------
# Tests for 452, 453, 503G & 503H all use these dataframes:

fake_eps__452_453_503G_503H_prev = pd.DataFrame(
    [
        {
            "CHILD": "101",
            "RNE": "S",
            "DECOM": "01/04/2020",
            "DEC": "04/06/2020",
            "PL_DISTANCE": 400,
            "PL_LA": "WAL",
        },
        {
            "CHILD": "101",
            "RNE": "P",
            "DECOM": "04/06/2020",
            "DEC": pd.NA,
            "PL_DISTANCE": 400,
            "PL_LA": "WAL",
        },
        {
            "CHILD": "103",
            "RNE": "P",
            "DECOM": "03/03/2020",
            "DEC": "10/07/2020",
            "PL_DISTANCE": 10,
            "PL_LA": "816",
        },
        {
            "CHILD": "103",
            "RNE": "L",
            "DECOM": "10/07/2020",
            "DEC": "09/12/2020",
            "PL_DISTANCE": 10,
            "PL_LA": "816",
        },
        {
            "CHILD": "104",
            "RNE": "B",
            "DECOM": "28/03/2020",
            "DEC": pd.NA,
            "PL_DISTANCE": 185,
            "PL_LA": "356",
        },
        {
            "CHILD": "105",
            "RNE": "L",
            "DECOM": "16/04/2020",
            "DEC": pd.NA,
            "PL_DISTANCE": "165",
            "PL_LA": "112",
        },
        {
            "CHILD": "106",
            "RNE": "S",
            "DECOM": "04/11/2020",
            "DEC": pd.NA,
            "PL_DISTANCE": "165",
            "PL_LA": "112",
        },
    ]
)

fake_eps__452_453_503G_503H = pd.DataFrame(
    [
        {
            "CHILD": "101",
            "RNE": "P",
            "DECOM": "04/06/2020",
            "DEC": "04/06/2021",
            "PL_DISTANCE": 400,
            "PL_LA": "WAL",
        },
        {
            "CHILD": "101",
            "RNE": "P",
            "DECOM": "04/06/2021",
            "DEC": pd.NA,
            "PL_DISTANCE": 400,
            "PL_LA": "WAL",
        },
        {
            "CHILD": "102",
            "RNE": "L",
            "DECOM": "20/12/2020",
            "DEC": "07/04/2021",
            "PL_DISTANCE": 10,
            "PL_LA": "816",
        },
        # Ignore all
        {
            "CHILD": "103",
            "RNE": "L",
            "DECOM": "02/02/2021",
            "DEC": pd.NA,
            "PL_DISTANCE": 10,
            "PL_LA": "816",
        },  # Ignore all
        {
            "CHILD": "104",
            "RNE": "B",
            "DECOM": "28/03/2020",
            "DEC": pd.NA,
            "PL_DISTANCE": 999.9,
            "PL_LA": "CON",
        },  # Fail all
        {
            "CHILD": "105",
            "RNE": "L",
            "DECOM": "16/04/2020",
            "DEC": pd.NA,
            "PL_DISTANCE": 165,
            "PL_LA": 112,
        },
        {
            "CHILD": "106",
            "RNE": "S",
            "DECOM": "04/11/2020",
            "DEC": pd.NA,
            "PL_DISTANCE": pd.NA,
            "PL_LA": pd.NA,
        },
        # Fail 452 and 503G only
    ]
)

fake_dfs__452_453_503G_503H = {
    "Episodes": fake_eps__452_453_503G_503H,
    "Episodes_last": fake_eps__452_453_503G_503H_prev,
}
