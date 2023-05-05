import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="542",
    message="A child aged under 10 at 31 March should not have conviction information completed.",
    affected_fields=["CONVICTED"],
)
def validate(dfs):
    if "OC2" not in dfs:
        return {}
    else:
        oc2 = dfs["OC2"]
        oc2["DOB"] = pd.todatetime(oc2["DOB"], format="%d/%m/%Y", errors="coerce")
        collectionend = pd.todatetime(
            dfs["metadata"]["collectionend"], format="%d/%m/%Y", errors="coerce"
        )
        errormask = (
            oc2["DOB"] + pd.offsets.DateOffset(years=10) > collectionend
        ) & oc2["CONVICTED"].notna()
        return {"OC2": oc2.index[errormask].tolist()}


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
