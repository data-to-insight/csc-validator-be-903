import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="460",
    message="Reason episode ceased is that child stayed with current carers at age 18 (or above), but child is aged under 18.",
    affected_fields=["DEC", "REC"],
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
        header["DOB18"] = header["DOB"] + pd.DateOffset(years=18)

        episodes = episodes[episodes["REC"] == "E17"]

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

        care_ended_under_18 = episodes_merged["DOB18"] > episodes_merged["DEC"]

        error_mask = care_ended_under_18

        error_locations = episodes.index[error_mask]

        return {"Episodes": error_locations.to_list()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "CHILD": ["101", "102", "101", "102", "103", "104"],
            "REC": ["E17", "E17", "X1", pd.NA, "E17", "E17"],
            "DEC": [
                "16/03/2023",
                "17/06/2020",
                "20/03/2020",
                pd.NA,
                "23/08/2020",
                "23/08/2020",
            ],
        }
    )

    fake_data_child = pd.DataFrame(
        {
            "CHILD": ["101", "102", "103", "104"],
            "DOB": ["16/03/2005", "23/09/2002", "31/12/2000", pd.NA],
        }
    )

    fake_dfs = {"Episodes": fake_data, "Header": fake_data_child}

    result = validate(fake_dfs)

    assert result == {"Episodes": [1]}
