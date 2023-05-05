import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="351",
    message="Child was over 21 at the start of the current collection year.",
    affected_fields=[
        "DOB",
    ],
)
def validate(dfs):
    if "Header" not in dfs:
        return {}

    else:
        header = dfs["Header"]
        collectionstart = dfs["metadata"]["collectionstart"]

        # Convert from string to date to appropriate format
        header["DOB"] = pd.todatetime(header["DOB"], format="%d/%m/%Y", errors="coerce")
        collectionstart = pd.todatetime(
            collectionstart, format="%d/%m/%Y", errors="coerce"
        )

        mask = collectionstart > (header["DOB"] + pd.DateOffset(years=21))
        # error locations
        headererrorlocs = header.index[mask]

        return {"Header": headererrorlocs.tolist()}


def test_validate():
    import pandas as pd

    fake_data_header = pd.DataFrame(
        {
            "CHILD": [
                "101",
                "102",
                "103",
                "104",
                "105",
            ],
            "DOB": [
                pd.NA,
                "11/11/2020",
                "03/10/1995",
                "01/04/2000",
                "01/01/1999",
            ],
        }
    )
    metadata = {
        "collection_start": "01/04/2021",
    }
    fake_dfs = {"Header": fake_data_header, "metadata": metadata}

    error_defn, error_func = validate()
    result = error_func(fake_dfs)

    assert result == {"Header": [2, 4]}
