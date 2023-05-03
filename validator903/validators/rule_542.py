import pandas as pd

from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="542",
        description="A child aged under 10 at 31 March should not have conviction information completed.",
        affected_fields=["CONVICTED"],
    )

    def _validate(dfs):
        if "OC2" not in dfs:
            return {}
        else:
            oc2 = dfs["OC2"]
            oc2["DOB"] = pd.to_datetime(oc2["DOB"], format="%d/%m/%Y", errors="coerce")
            collection_end = pd.to_datetime(
                dfs["metadata"]["collection_end"], format="%d/%m/%Y", errors="coerce"
            )
            error_mask = (
                oc2["DOB"] + pd.offsets.DateOffset(years=10) > collection_end
            ) & oc2["CONVICTED"].notna()
            return {"OC2": oc2.index[error_mask].to_list()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "DOB": ["08/03/2020", "22/06/2000", pd.NA, "13/10/2000", "10/01/2017"],
            "CONVICTED": [1, pd.NA, 1, 1, 1],  # 0 , 4
        }
    )

    metadata = {"collection_end": "31/03/2020"}

    fake_dfs = {"OC2": fake_data, "metadata": metadata}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"OC2": [0, 4]}
