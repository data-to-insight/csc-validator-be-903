import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="391",
    message="Young person was not 17, 18, 19, 20 or 21 during the current collection year. ",
    affected_fields=["DOB", "IN_TOUCH", "ACTIV", "ACCOM"],
)
def validate(dfs):
    if "OC3" not in dfs:
        return {}
    else:
        oc3 = dfs["OC3"]
        collectionend = dfs["metadata"]["collectionend"]

        # convert dates to datetime format
        oc3["DOB"] = pd.todatetime(oc3["DOB"], format="%d/%m/%Y", errors="coerce")
        collectionend = pd.todatetime(collectionend, format="%d/%m/%Y", errors="coerce")

        # If <DOB> < 17 years prior to <COLLECTIONENDDATE> then <INTOUCH>, <ACTIV> and <ACCOM> should not be provided
        checkage = oc3["DOB"] + pd.offsets.DateOffset(years=17) > collectionend
        mask = checkage & (
            oc3["INTOUCH"].notna() | oc3["ACTIV"].notna() | oc3["ACCOM"].notna()
        )
        # Then raise an error if either INTOUCH, ACTIV, or ACCOM have been provided too

        # error locations
        oc3errorlocs = oc3.index[mask]

        return {"OC3": oc3errorlocs.tolist()}


def test_validate():
    import pandas as pd

    fake_data_oc3 = pd.DataFrame(
        {
            "CHILD": ["A", "B", "C", "D", "E"],
            "DOB": [
                "01/01/2001",
                "01/01/2016",
                "20/12/1997",
                "01/01/2002",
                "03/01/2004",
            ],
            "IN_TOUCH": ["DIED", "Yes", "RHOM", pd.NA, pd.NA],
            "ACTIV": [pd.NA, pd.NA, "XXX", pd.NA, pd.NA],
            "ACCOM": [pd.NA, pd.NA, pd.NA, "XXX", pd.NA],
        }
    )
    metadata = {"collection_end": "31/03/2018"}

    fake_dfs = {"OC3": fake_data_oc3, "metadata": metadata}
    error_defn, error_func = validate()
    result = error_func(fake_dfs)
    assert result == {"OC3": [1, 3]}
