from validator903.types import ErrorDefinition


@rule_definition(
    code="204",
    message="Ethnic origin code disagrees with the ethnic origin already recorded for this child.",
    affected_fields=["ETHNIC"],
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
        ethnicisdifferent = (
            headermerged["ETHNIC"].astype(str).str.upper()
            != headermerged["ETHNIClast"].astype(str).str.upper()
        )

        errormask = inbothyears & ethnicisdifferent

        errorlocations = header.index[errormask]

        return {"Header": errorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "CHILD": ["101", "102", "103", "104", "105", "106", "108", "109", "110"],
            "ETHNIC": [
                "WBRI",
                "WBRI",
                "nobt",
                "AINS",
                pd.NA,
                "BOTH",
                pd.NA,
                "BCRB",
                "MWBC",
            ],
        }
    )

    fake_data_prev = pd.DataFrame(
        {
            "CHILD": ["101", "102", "103", "104", "105", "107", "108", "109", "110"],
            "ETHNIC": [
                "WBRI",
                "NOBT",
                "NOBT",
                "AINS",
                pd.NA,
                "REFU",
                "MOTH",
                pd.NA,
                "MWBA",
            ],
        }
    )

    fake_dfs = {"Header": fake_data, "Header_last": fake_data_prev}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Header": [1, 6, 7, 8]}
