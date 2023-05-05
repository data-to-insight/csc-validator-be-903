import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="203",
    message="Date of birth disagrees with the date of birth already recorded for this child.",
    affected_fields=["DOB"],
)
def validate(dfs):
    if "Header" not in dfs or "Headerlast" not in dfs:
        return {}
    else:
        header = dfs["Header"]
        headerlast = dfs["Headerlast"]

        header["DOB"] = pd.todatetime(header["DOB"], format="%d/%m/%Y", errors="coerce")
        headerlast["DOB"] = pd.todatetime(
            headerlast["DOB"], format="%d/%m/%Y", errors="coerce"
        )

        headermerged = (
            header.resetindex()
            .merge(
                headerlast,
                how="left",
                on=["CHILD"],
                suffixes=("", "last"),
                indicator=True,
            )
            .setindex("index")
        )

        inbothyears = headermerged["merge"] == "both"
        dobisdifferent = headermerged["DOB"].astype(str) != headermerged[
            "DOBlast"
        ].astype(str)

        errormask = inbothyears & dobisdifferent

        errorlocations = header.index[errormask]

        return {"Header": errorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "CHILD": ["101", "102", "103", "104", "105", "106", "108", "109", "110"],
            "DOB": [
                "16/03/2020",
                "23/09/2016",
                "31/12/19",
                "31/02/2018",
                pd.NA,
                "10/08/2014",
                pd.NA,
                "20/01/2017",
                "31/06/2020",
            ],
        }
    )

    fake_data_prev = pd.DataFrame(
        {
            "CHILD": ["101", "102", "103", "104", "105", "107", "108", "109", "110"],
            "DOB": [
                "16/03/2020",
                "22/09/2016",
                "31/12/2019",
                "31/02/2018",
                pd.NA,
                "11/11/2021",
                "04/06/2017",
                pd.NA,
                "30/06/2020",
            ],
        }
    )

    fake_dfs = {"Header": fake_data, "Header_last": fake_data_prev}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Header": [1, 2, 6, 7, 8]}
