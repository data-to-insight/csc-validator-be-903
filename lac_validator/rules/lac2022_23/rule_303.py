import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="303",
    message="If date Unaccompanied Asylum-Seeking Child (UASC) status ceased is not null, UASC status must be coded 1.",
    affected_fields=["DUC", "UASC"],
    tables=["UASC", "Header"],
)
def validate(dfs):
    if ("UASC" not in dfs) or ("Header" not in dfs):
        return {}
    elif "UASC" not in dfs["Header"].columns:
        return {}
    else:
        uasc = dfs["UASC"]
        header = dfs["Header"]

        # merge
        uasc.reset_index(inplace=True)
        header.reset_index(inplace=True)

        merged = header.merge(uasc, how="left", on="CHILD", suffixes=["_er", "_sc"])

        merged["UASC"] = pd.to_numeric(merged["UASC"], errors="coerce")

        # If <DUC> provided, then <UASC> must be '1'
        error_mask = merged["DUC"].notna() & (merged["UASC"] != 1)

        uasc_error_locs = merged.loc[error_mask, "index_sc"]
        header_error_locs = merged.loc[error_mask, "index_er"]

        return {
            "UASC": uasc_error_locs.tolist(),
            "Header": header_error_locs.tolist(),
        }


def test_validate():
    import pandas as pd

    fake_data_uasc = pd.DataFrame(
        {
            "CHILD": [
                0,
                1,
                2,
                3,
                4,
                5,
            ],
            "DUC": [
                pd.NA,
                "04/04/2021",
                "01/06/2020",
                pd.NA,
                "10/04/2020",
                "01/03/2021",
            ],
        }
    )
    fake_data_header = pd.DataFrame(
        {
            "CHILD": [
                0,
                1,
                2,
                3,
                4,
                5,
            ],
            "UASC": [0, 1, 0, "1", "0", 1],
        }
    )

    fake_dfs = {"UASC": fake_data_uasc, "Header": fake_data_header}

    result = validate(fake_dfs)

    assert result == {"UASC": [2, 4], "Header": [2, 4]}
