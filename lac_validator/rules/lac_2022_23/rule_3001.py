import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="3001",
    message="Where care leavers information is being returned for a young person around their 17th birthday, the accommodation cannot be with their former foster carer(s).",
    affected_fields=["REC"],
)
def validate(dfs):
    if "Header" not in dfs:
        return {}
    if "OC3" not in dfs:
        return {}
    else:
        header = dfs["Header"]
        oc3 = dfs["OC3"]
        collectionstart = pd.todatetime(
            dfs["metadata"]["collectionstart"], format="%d/%m/%Y", errors="coerce"
        )
        collectionend = pd.todatetime(
            dfs["metadata"]["collectionend"], format="%d/%m/%Y", errors="coerce"
        )

        header["DOB"] = pd.todatetime(header["DOB"], format="%d/%m/%Y", errors="coerce")
        header["DOB17"] = header["DOB"] + pd.DateOffset(years=17)

        oc3merged = (
            oc3.resetindex()
            .merge(
                header,
                how="left",
                on=["CHILD"],
                suffixes=("", "header"),
                indicator=True,
            )
            .setindex("index")
        )

        accomfoster = oc3merged["ACCOM"].str.upper().astype(str).isin(["Z1", "Z2"])
        age17inyear = (oc3merged["DOB17"] <= collectionend) & (
            oc3merged["DOB17"] >= collectionstart
        )

        errormask = accomfoster & age17inyear

        errorlocations = oc3.index[errormask]

        return {"OC3": errorlocations.tolist()}


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
