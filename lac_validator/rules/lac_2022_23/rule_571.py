import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="571",
    message="The date that the child ceased to be missing or away from placement without authorisation is before the start or after the end of the collection year.",
    affected_fields=["MIS_END"],
)
def validate(dfs):
    if "Missing" not in dfs:
        return {}
    else:
        missing = dfs["Missing"]
        collectionstart = pd.todatetime(
            dfs["metadata"]["collectionstart"], format="%d/%m/%Y", errors="coerce"
        )
        collectionend = pd.todatetime(
            dfs["metadata"]["collectionend"], format="%d/%m/%Y", errors="coerce"
        )

        missing["fMISEND"] = pd.todatetime(
            missing["MISEND"], format="%d/%m/%Y", errors="coerce"
        )

        enddatebeforeyear = missing["fMISEND"] < collectionstart
        enddateafteryear = missing["fMISEND"] > collectionend

        errormask = enddatebeforeyear | enddateafteryear

        errorlocations = missing.index[errormask]

        return {"Missing": errorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "MIS_START": [
                "08/03/2020",
                "22/06/2020",
                pd.NA,
                "13/10/2021",
                "10/24/2021",
            ],
            "MIS_END": ["08/03/2020", pd.NA, "22/06/2020", "13/10/21", pd.NA],
        }
    )

    metadata = {"collection_start": "01/04/2020", "collection_end": "31/03/2020"}

    fake_dfs = {"Missing": fake_data, "metadata": metadata}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Missing": [0, 2]}
