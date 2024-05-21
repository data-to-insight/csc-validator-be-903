import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="391",
    message="Young person was not 17, 18, 19, 20 or 21 during the current collection year. ",
    affected_fields=["DOB", "IN_TOUCH", "ACTIV", "ACCOM"],
    tables=["OC3"],
)
def validate(dfs):
    if "OC3" not in dfs:
        return {}
    else:
        oc3 = dfs["OC3"]
        collection_end = dfs["metadata"]["collection_end"]

        # convert dates to datetime format
        oc3["DOB"] = pd.to_datetime(oc3["DOB"], format="%d/%m/%Y", errors="coerce")
        collection_end = pd.to_datetime(
            collection_end, format="%d/%m/%Y", errors="coerce"
        )

        # If <DOB> < 17 years prior to <COLLECTION_END_DATE> then <IN_TOUCH>, <ACTIV> and <ACCOM> should not be provided
        check_age = oc3["DOB"] + pd.offsets.DateOffset(years=17) > collection_end
        mask = check_age & (
            oc3["IN_TOUCH"].notna() | oc3["ACTIV"].notna() | oc3["ACCOM"].notna()
        )
        # Then raise an error if either IN_TOUCH, ACTIV, or ACCOM have been provided too

        # error locations
        oc3_error_locs = oc3.index[mask]

        return {"OC3": oc3_error_locs.tolist()}


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

    result = validate(fake_dfs)
    assert result == {"OC3": [1, 3]}
