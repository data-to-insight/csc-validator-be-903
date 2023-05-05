import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="104",
    message="Date for Unaccompanied Asylum-Seeking Children (UASC) status ceased is not a valid date.",
    affected_fields=["DUC"],
)
def validate(dfs):
    if "UASC" not in dfs:
        return {}
    else:
        uasc = dfs["UASC"]
        uasc["DUCdt"] = pd.todatetime(uasc["DUC"], format="%d/%m/%Y", errors="coerce")
        collectionstart = pd.todatetime(
            dfs["metadata"]["collectionstart"], format="%d/%m/%Y", errors="coerce"
        )
        mask = (uasc["DUCdt"].isna() & uasc["DUC"].notna()) | (
            uasc["DUCdt"] < collectionstart
        )

        return {"UASC": uasc.index[mask].tolist()}


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
