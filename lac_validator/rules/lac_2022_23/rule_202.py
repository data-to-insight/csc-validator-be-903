from validator903.types import ErrorDefinition


@rule_definition(
    code="202",
    message="The gender code conflicts with the gender already recorded for this child.",
    affected_fields=["SEX"],
)
def validate(dfs):
    if "Header" not in dfs or "Headerlast" not in dfs:
        return {}
    else:
        header = dfs["Header"]
        headerlast = dfs["Headerlast"]

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
        sexisdifferent = headermerged["SEX"].astype(str) != headermerged[
            "SEXlast"
        ].astype(str)

        errormask = inbothyears & sexisdifferent

        errorlocations = headermerged.index[errormask]

        return {"Header": errorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "CHILD": ["101", "102", "103", "104", "105", "106", "108", "109", "110"],
            "SEX": ["1", 2, "1", "2", pd.NA, "1", pd.NA, "2", "3"],
        }
    )

    fake_data_prev = pd.DataFrame(
        {
            "CHILD": ["101", "102", "103", "104", "105", "107", "108", "109", "110"],
            "SEX": ["1", 1, "2", 2, pd.NA, "1", "2", pd.NA, "2"],
        }
    )

    fake_dfs = {"Header": fake_data, "Header_last": fake_data_prev}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Header": [1, 2, 6, 7, 8]}
