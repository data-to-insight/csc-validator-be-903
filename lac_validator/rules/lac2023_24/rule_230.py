import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="230",
    message="Ofsted Unique reference number (URN) is required for any English H5 placements from 28 October 2023.",
    affected_fields=["PLACE", "DEC", "URN"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        episodes["DEC"] = pd.to_datetime(
            episodes["DEC"], format="%d/%m/%Y", errors="coerce"
        )
        max_dec_allowed = pd.to_datetime(
            "28/10/2023", format="%d/%m/%Y", errors="coerce"
        )

        out_of_england = (
            episodes["PL_LA"].astype("str").str.upper().str.startswith(("N", "W", "S"))
        )

        mask = (
            episodes["PLACE"].isin(["H5"])
            & ((episodes["DEC"] >= max_dec_allowed) | episodes["DEC"].isna())
            & (episodes["URN"].isna() | (episodes["URN"] == "XXXXXXX"))
            & ~out_of_england
        )

        validation_error_mask = mask
        validation_error_locations = episodes.index[validation_error_mask]

        return {"Episodes": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "PLACE": ["H5", "H5", "H5", "H5", "P1", "H5"],
            "DEC": ["28/10/2023", "28/10/2023", pd.NA, pd.NA, pd.NA, pd.NA],
            "PL_LA": ["A1", "A1", "A1", "S1", "A1", "A1"],
            "URN": [pd.NA, "X1", pd.NA, pd.NA, pd.NA, "XXXXXXX"]
            # 0 Fail (DEC on/after validation date and no URN)
            # 1 Pass (DEC on/after validation date with URN)
            # 2 Fail (Nil DEC and no URN)
            # 3 Ignore (Nil DEC and no URN *but* outside England)
            # 4 Ignore (Nil DEC and no URN *but* not H5)
            # 5 Fail (Nil DEC and URN is XXXXXXX)
        }
    )

    fake_dfs = {"Episodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"Episodes": [0, 2, 5]}
