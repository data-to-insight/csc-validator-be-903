import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="301",
    message="Date of birth falls after the year ended.",
    affected_fields=["DOB"],
    tables=["Header"],
)
def validate(dfs):
    if "Header" not in dfs:
        return {}
    else:
        header = dfs["Header"]
        collection_end = dfs["metadata"]["collection_end"]

        # convert dates
        collection_end = pd.to_datetime(
            collection_end, format="%d/%m/%Y", errors="coerce"
        )
        header["DOB"] = pd.to_datetime(
            header["DOB"], format="%d/%m/%Y", errors="coerce"
        )

        # <DOB> must be <= <COLLECTION_END_DATE>
        mask = header["DOB"] > collection_end

        # error locations
        error_locs = header.index[mask]
        return {"Header": error_locs.tolist()}


def test_validate():
    import pandas as pd

    fake_data_header = pd.DataFrame(
        [
            {
                "CHILD": 101,
                "DOB": "01/07/2021",
            },  # 0 fail
            {
                "CHILD": 102,
                "DOB": "02/06/2000",
            },  # 1
            {
                "CHILD": 103,
                "DOB": "03/06/2000",
            },  # 2
            {
                "CHILD": 104,
                "DOB": "04/06/2022",
            },  # 3 fail
            {
                "CHILD": 105,
                "DOB": pd.NA,
            },  # 4
        ]
    )

    metadata = {"collection_start": "01/04/2020", "collection_end": "31/03/2021"}

    fake_dfs = {"Header": fake_data_header, "metadata": metadata}

    result = validate(fake_dfs)
    assert result == {"Header": [0, 3]}
