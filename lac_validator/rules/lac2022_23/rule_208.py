import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="208",
    message="Unique Pupil Number (UPN) for the current year disagrees with the Unique Pupil Number (UPN) already recorded for this child.",
    affected_fields=["UPN"],
)
def validate(dfs):
    if "Header" not in dfs or "Header_last" not in dfs:
        return {}
    else:
        header = dfs["Header"]
        header_last = dfs["Header_last"]

        header_merged = (
            header.reset_index()
            .merge(
                header_last,
                how="left",
                on=["CHILD"],
                suffixes=("", "_last"),
                indicator=True,
            )
            .set_index("index")
        )

        null_now = header_merged["UPN"].isna()
        null_before = header_merged["UPN_last"].isna()
        in_both_years = header_merged["_merge"] == "both"

        header_merged["UPN"] = header_merged["UPN"].astype(str).str.upper()
        header_merged["UPN_last"] = header_merged["UPN_last"].astype(str).str.upper()
        upn_is_different = (
            (header_merged["UPN"] != header_merged["UPN_last"])
            & ~(null_now & null_before)
            # exclude case where unknown both years null; leave to 442 (missing UPN)
        )

        UN2_to_5 = ["UN2", "UN3", "UN4", "UN5"]
        UN_codes = [
            "UN1",
        ] + UN2_to_5
        valid_unknown_change = (
            (
                header_merged["UPN_last"].eq("UN1") | null_before
            )  # change from UN1/null...
            & header_merged["UPN"].isin(UN2_to_5)
        ) | (  # ...to UN2-5
            null_before & header_merged["UPN_last"].eq("UN1")
        )  # OR, change from null to UN1
        unknown_to_known = (
            header_merged["UPN_last"].isin(UN_codes) | null_before
        ) & ~(  # was either null or an UN-code
            header_merged["UPN"].isin(UN_codes) | null_now
        )  # now neither null nor UN-known

        error_mask = (
            in_both_years & upn_is_different & ~valid_unknown_change & ~unknown_to_known
        )

        error_locations = header.index[error_mask]

        return {"Header": error_locations.to_list()}


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

    result = validate(fake_dfs)

    assert result == {"Header": [1, 5, 6, 12]}
