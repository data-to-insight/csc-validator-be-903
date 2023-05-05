from validator903.types import ErrorDefinition


@rule_definition(
    code="208",
    message="Unique Pupil Number (UPN) for the current year disagrees with the Unique Pupil Number (UPN) already recorded for this child.",
    affected_fields=["UPN"],
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

        nullnow = headermerged["UPN"].isna()
        nullbefore = headermerged["UPNlast"].isna()
        inbothyears = headermerged["merge"] == "both"

        headermerged["UPN"] = headermerged["UPN"].astype(str).str.upper()
        headermerged["UPNlast"] = headermerged["UPNlast"].astype(str).str.upper()
        upnisdifferent = (
            (headermerged["UPN"] != headermerged["UPNlast"])
            & ~(nullnow & nullbefore)
            # exclude case where unknown both years null; leave to 442 (missing UPN)
        )

        UN2to5 = ["UN2", "UN3", "UN4", "UN5"]
        UNcodes = [
            "UN1",
        ] + UN2to5
        validunknownchange = (
            (headermerged["UPNlast"].eq("UN1") | nullbefore)  # change from UN1/null...
            & headermerged["UPN"].isin(UN2to5)
        ) | (  # ...to UN2-5
            nullbefore & headermerged["UPNlast"].eq("UN1")
        )  # OR, change from null to UN1
        unknowntoknown = (
            headermerged["UPNlast"].isin(UNcodes) | nullbefore
        ) & ~(  # was either null or an UN-code
            headermerged["UPN"].isin(UNcodes) | nullnow
        )  # now neither null nor UN-known

        errormask = inbothyears & upnisdifferent & ~validunknownchange & ~unknowntoknown

        errorlocations = header.index[errormask]

        return {"Header": errorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data_prev = pd.DataFrame(
        {
            "CHILD": [
                "101",
                "102",
                "103",
                "104",
                "105",
                "106",
                "108",
                "109",
                "110",
                "111",
                "33333",
                "44444",
                "1000",
            ],
            "UPN": [
                "UN5",
                "X888888888888",
                "UN1",
                "UN1",
                pd.NA,
                "UN4",
                "UN1",
                pd.NA,
                "a------------",
                "UN2",
                "UN5",
                "H000000000000",
                pd.NA,
            ],
        }
    )
    fake_data = pd.DataFrame(
        {
            "CHILD": [
                "101",
                "102",
                "103",
                "104",
                "105",
                "106",
                "108",
                "109",
                "110",
                "111",
                "55555",
                "66666",
                "1000",
            ],
            "UPN": [
                "H801200001001",
                "O------------",
                "UN1",
                "UN2",
                pd.NA,
                "UN3",
                pd.NA,
                "UN4",
                "A------------",
                "H801200001111",
                "UN5",
                "X999999999999",
                "UN1",
            ],
        }
    )

    fake_dfs = {"Header": fake_data, "Header_last": fake_data_prev}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Header": [1, 5, 6, 12]}
