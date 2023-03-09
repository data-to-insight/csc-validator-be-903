import pandas as pd

from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="602",
        description="The episode data submitted for this child does not show that he/she was adopted during the year.",
        affected_fields=["CHILD"],
    )

    def _validate(dfs):
        if "Episodes" not in dfs or "AD1" not in dfs:
            return {}
        else:
            epi = dfs["Episodes"]
            ad1 = dfs["AD1"]
            epi["DEC"] = pd.to_datetime(epi["DEC"], format="%d/%m/%Y", errors="coerce")
            collection_start = pd.to_datetime(
                dfs["metadata"]["collection_start"], format="%d/%m/%Y", errors="coerce"
            )
            collection_end = pd.to_datetime(
                dfs["metadata"]["collection_end"], format="%d/%m/%Y", errors="coerce"
            )

            mask1 = (epi["DEC"] <= collection_end) & (epi["DEC"] >= collection_start)
            mask2 = epi["REC"].isin(["E11", "E12"])
            adoption_eps = epi[mask1 & mask2]

            adoption_fields = [
                "DATE_INT",
                "DATE_MATCH",
                "FOSTER_CARE",
                "NB_ADOPTR",
                "SEX_ADOPTR",
                "LS_ADOPTR",
            ]

            err_list = (
                ad1.reset_index()
                .merge(adoption_eps, how="left", on="CHILD", indicator=True)
                .query("_merge == 'left_only'")
                .dropna(subset=adoption_fields, how="all")
                .set_index("index")
                .index.unique()
                .to_list()
            )

            return {"AD1": err_list}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_epi = pd.DataFrame(
        {
            "CHILD": ["111", "222", "333", "444", "555", "666", "888"],
            "DEC": [
                "08/06/2020",
                "09/07/2020",
                "09/08/2020",
                "25/03/2021",
                "22/03/2020",
                "25/04/2021",
                pd.NA,
            ],
            "REC": ["E11", "oo", "T4", "E11", "oo", pd.NA, "E11"],
        }
    )
    fake_ad1 = pd.DataFrame(
        {
            "CHILD": ["111", "123", "222", "333", "345", "444", "555", "666", "777"],
            "DATE_INT": [pd.NA, "xx", pd.NA, pd.NA, "xx", "oo", pd.NA, "xx", "xx"],
        }
    )

    other_than_DATE_INT = [
        "DATE_MATCH",
        "FOSTER_CARE",
        "NB_ADOPTR",
        "SEX_ADOPTR",
        "LS_ADOPTR",
    ]

    for c in other_than_DATE_INT:
        fake_ad1[c] = pd.NA

    metadata = {"collection_start": "01/04/2020", "collection_end": "31/03/2021"}

    fake_dfs = {"Episodes": fake_epi, "AD1": fake_ad1, "metadata": metadata}

    error_defn, error_func = validate()

    assert error_func(fake_dfs) == {"AD1": [1, 4, 7, 8]}
