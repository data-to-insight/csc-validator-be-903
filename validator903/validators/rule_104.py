import pandas as pd

from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="104",
        description="Date for Unaccompanied Asylum-Seeking Children (UASC) status ceased is not a valid date.",
        affected_fields=["DUC"],
    )

    def _validate(dfs):
        if "UASC" not in dfs:
            return {}
        else:
            uasc = dfs["UASC"]
            uasc["DUC_dt"] = pd.to_datetime(
                uasc["DUC"], format="%d/%m/%Y", errors="coerce"
            )
            collection_start = pd.to_datetime(
                dfs["metadata"]["collection_start"], format="%d/%m/%Y", errors="coerce"
            )
            mask = (uasc["DUC_dt"].isna() & uasc["DUC"].notna()) | (
                uasc["DUC_dt"] < collection_start
            )

            return {"UASC": uasc.index[mask].to_list()}

    return error, _validate


# !# False positives if child was UASC in last 2 years but data not provided


def test_validate():
    import pandas as pd

    fake_uasc = pd.DataFrame(
        {
            "DUC": [
                "01/03/2019",
                "19/02/2020",
                "03/04/2019",
                "01/01/2019",
                pd.NA,
                "INNVLAID/DATE/2077",
            ],
        }
    )

    metadata = {"collection_start": "01/04/2019"}

    fake_dfs = {"UASC": fake_uasc, "metadata": metadata}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)
    assert result == {"UASC": [0, 3, 5]}
