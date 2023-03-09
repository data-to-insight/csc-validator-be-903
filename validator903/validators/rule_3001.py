import pandas as pd

from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="3001",
        description="Where care leavers information is being returned for a young person around their 17th birthday, the accommodation cannot be with their former foster carer(s).",
        affected_fields=["REC"],
    )

    def _validate(dfs):
        if "Header" not in dfs:
            return {}
        if "OC3" not in dfs:
            return {}
        else:
            header = dfs["Header"]
            oc3 = dfs["OC3"]
            collection_start = pd.to_datetime(
                dfs["metadata"]["collection_start"], format="%d/%m/%Y", errors="coerce"
            )
            collection_end = pd.to_datetime(
                dfs["metadata"]["collection_end"], format="%d/%m/%Y", errors="coerce"
            )

            header["DOB"] = pd.to_datetime(
                header["DOB"], format="%d/%m/%Y", errors="coerce"
            )
            header["DOB17"] = header["DOB"] + pd.DateOffset(years=17)

            oc3_merged = (
                oc3.reset_index()
                .merge(
                    header,
                    how="left",
                    on=["CHILD"],
                    suffixes=("", "_header"),
                    indicator=True,
                )
                .set_index("index")
            )

            accom_foster = (
                oc3_merged["ACCOM"].str.upper().astype(str).isin(["Z1", "Z2"])
            )
            age_17_in_year = (oc3_merged["DOB17"] <= collection_end) & (
                oc3_merged["DOB17"] >= collection_start
            )

            error_mask = accom_foster & age_17_in_year

            error_locations = oc3.index[error_mask]

            return {"OC3": error_locations.to_list()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "CHILD": ["101", "102", "101", "102", "103", "102"],
            "ACCOM": ["Z1", "Z2", "T1", pd.NA, "Z1", "Z3"],
        }
    )

    fake_data_child = pd.DataFrame(
        {
            "CHILD": ["101", "102", "103"],
            "DOB": ["16/03/2004", "23/09/2003", "31/12/2006"],
        }
    )

    metadata = {"collection_start": "01/04/2020", "collection_end": "31/03/2021"}

    fake_dfs = {"OC3": fake_data, "Header": fake_data_child, "metadata": metadata}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"OC3": [0, 1]}
