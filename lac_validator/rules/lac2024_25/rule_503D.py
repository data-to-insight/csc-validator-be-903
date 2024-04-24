import pandas as pd

from lac_validator.rule_engine import rule_definition
from lac_validator.rules.rule_utils import field_different_from_previous


@rule_definition(
    code="503D",
    message="The placement type in the first episode does not match open episode at end of last year",
    affected_fields=["PLACE"],
)
def validate(dfs):
    diff_prev = field_different_from_previous(dfs, field="PLACE")

    return diff_prev

def test_validate():
    fake_epi = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "DEC": pd.NA,
                "DECOM": "01/06/2020",
                "PLACE": "T1",
            },  # 0  Fails
            {"CHILD": "111", "DEC": pd.NA, "DECOM": "05/06/2020", "PLACE": "T2"},  # 1
            {"CHILD": "111", "DEC": pd.NA, "DECOM": "06/06/2020", "PLACE": "T3"},  # 2
            {
                "CHILD": "123",
                "DEC": pd.NA,
                "DECOM": "08/06/2020",
                "PLACE": "T4",
            },  # 3  Fails
            {
                "CHILD": "222",
                "DEC": pd.NA,
                "DECOM": "05/06/2020",
                "PLACE": "T5",
            },  # 4  Fails
            {
                "CHILD": "333",
                "DEC": pd.NA,
                "DECOM": "06/06/2020",
                "PLACE": "T6",
            },  # 5  Fails
            {"CHILD": "333", "DEC": pd.NA, "DECOM": "07/06/2020", "PLACE": "T7"},  # 6
            {"CHILD": "444", "DEC": pd.NA, "DECOM": "08/06/2020", "PLACE": "T3"},  # 7
            {"CHILD": "555", "DEC": pd.NA, "DECOM": "08/06/2020", "PLACE": "K3"}  # 7
        ]
    )

    fake_epi_last = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "DEC": pd.NA,
                "DECOM": "01/06/2020",
                "PLACE": pd.NA,
            },  # Max
            {"CHILD": "123", "DEC": pd.NA, "DECOM": "08/06/2020", "PLACE": "N4"},  # Max
            {"CHILD": "222", "DEC": pd.NA, "DECOM": "05/06/2020", "PLACE": "L"},  # Max
            {
                "CHILD": "333",
                "DEC": pd.NA,
                "DECOM": "06/06/2020",
                "PLACE": pd.NA,
            },  # Max
            {"CHILD": "444", "DEC": pd.NA, "DECOM": "08/06/2020", "PLACE": "L"},
            {"CHILD": "444", "DEC": pd.NA, "DECOM": "09/06/2020", "PLACE": "L"},
            {"CHILD": "444", "DEC": pd.NA, "DECOM": "19/06/2020", "PLACE": "L"},  # Max
            {"CHILD": "555", "DEC": pd.NA, "DECOM": "19/06/2020", "PLACE": "H5"}
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

    fake_dfs = {"Episodes": fake_epi, "Episodes_last": fake_epi_last}

    result = validate(fake_dfs)

    assert result == {"Episodes": [0, 3, 4, 5, 7]}
