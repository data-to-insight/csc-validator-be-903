import pandas as pd

from lac_validator.rule_engine import rule_definition
from lac_validator.rules.rule_utils import field_different_from_previous


@rule_definition(
    code="503E",
    message="The placement provider in the first episode does not match open episode at end of last year.",
    affected_fields=["PLACE_PROVIDER"],
)
def validate(dfs):
    return field_different_from_previous(dfs, field="PLACE_PROVIDER")


def test_validate():
    fake_epi = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "DEC": pd.NA,
                "DECOM": "01/06/2020",
                "PLACE_PROVIDER": "PR1",
            },  # 0  Fails
            {
                "CHILD": "111",
                "DEC": pd.NA,
                "DECOM": "05/06/2020",
                "PLACE_PROVIDER": "PR2",
            },  # 1
            {
                "CHILD": "111",
                "DEC": pd.NA,
                "DECOM": "06/06/2020",
                "PLACE_PROVIDER": "PR3",
            },  # 2
            {
                "CHILD": "123",
                "DEC": pd.NA,
                "DECOM": "08/06/2020",
                "PLACE_PROVIDER": "PR4",
            },  # 3
            {
                "CHILD": "222",
                "DEC": pd.NA,
                "DECOM": "05/06/2020",
                "PLACE_PROVIDER": "PR5",
            },  # 4  Fails
            {
                "CHILD": "333",
                "DEC": pd.NA,
                "DECOM": "06/06/2020",
                "PLACE_PROVIDER": "PR0",
            },  # 5  Fails
            {
                "CHILD": "333",
                "DEC": pd.NA,
                "DECOM": "07/06/2020",
                "PLACE_PROVIDER": "PR1",
            },  # 6
            {
                "CHILD": "444",
                "DEC": pd.NA,
                "DECOM": "05/06/2020",
                "PLACE_PROVIDER": "PR3",
            },  # 7
        ]
    )

    fake_epi_last = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "DEC": pd.NA,
                "DECOM": "01/06/2020",
                "PLACE_PROVIDER": pd.NA,
            },  # Max
            {
                "CHILD": "123",
                "DEC": pd.NA,
                "DECOM": "08/06/2020",
                "PLACE_PROVIDER": "PR4",
            },  # Max
            {
                "CHILD": "222",
                "DEC": pd.NA,
                "DECOM": "05/06/2020",
                "PLACE_PROVIDER": "PR2",
            },  # Max
            {
                "CHILD": "333",
                "DEC": pd.NA,
                "DECOM": "06/06/2020",
                "PLACE_PROVIDER": pd.NA,
            },  # Max
            {
                "CHILD": "444",
                "DEC": pd.NA,
                "DECOM": "08/06/2020",
                "PLACE_PROVIDER": "PR1",
            },
            {
                "CHILD": "444",
                "DEC": pd.NA,
                "DECOM": "09/06/2020",
                "PLACE_PROVIDER": "PR0",
            },
            {
                "CHILD": "444",
                "DEC": pd.NA,
                "DECOM": "19/06/2020",
                "PLACE_PROVIDER": "PR2",
            },  # Max
        ]
    )

    fake_epi["DECOM"] = pd.to_datetime(
        fake_epi["DECOM"], format="%d/%m/%Y", errors="coerce"
    )
    fake_epi_last["DECOM"] = pd.to_datetime(
        fake_epi_last["DECOM"], format="%d/%m/%Y", errors="coerce"
    )
    fake_epi_last["DEC"] = pd.to_datetime(
        fake_epi_last["DEC"], format="%d/%m/%Y", errors="coerce"
    )
    # For the test, this doesn't affect anything except how the data is handled
    # by the field_different function, so it doesn't matter that the years
    # in the test dfs are not accurate to this collection year
    # As seen in conftest collection year is read in as XXXX/XX and stored in metadata
    # as the first four characters using [:4] in _process_metadata in datastore```
    metadata = {"collectionYear": "2022"}

    fake_dfs = {
        "Episodes": fake_epi,
        "Episodes_last": fake_epi_last,
        "metadata": metadata,
    }

    result = validate(fake_dfs)

    assert result == {"Episodes": [0, 4, 5, 7]}
