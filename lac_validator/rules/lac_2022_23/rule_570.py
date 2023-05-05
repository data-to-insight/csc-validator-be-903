import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="570",
    message="The date that the child started to be missing or away from placement without authorisation is after the end of the collection year.",
    affected_fields=["MIS_START"],
)
def validate(dfs):
    if "Missing" not in dfs:
        return {}
    else:
        mis = dfs["Missing"]
        collectionend = pd.todatetime(
            dfs["metadata"]["collectionend"], format="%d/%m/%Y", errors="coerce"
        )

        mis["MISSTART"] = pd.todatetime(
            mis["MISSTART"], format="%d/%m/%Y", errors="coerce"
        )
        errormask = mis["MISSTART"] > collectionend

        return {"Missing": mis.index[errormask].tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "MIS_START": [
                "08/04/2020",
                "22/06/2020",
                pd.NA,
                "13/10/2005",
                "10/05/2001",
            ],
        }
    )

    metadata = {"collection_end": "31/03/2020"}

    fake_dfs = {"Missing": fake_data, "metadata": metadata}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Missing": [0, 1]}
