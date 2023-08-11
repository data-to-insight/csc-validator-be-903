import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="365",
    message="Any individual short- term respite placement must not exceed 17 days.",
    affected_fields=["LS", "DECOM", "DEC"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    episodes = dfs["Episodes"]
    collection_end_str = dfs["metadata"]["collection_end"]

    episodes.loc[episodes["DEC"].isna(), "DEC"] = collection_end_str
    episodes["DECOM"] = pd.to_datetime(
        episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
    )
    episodes["DEC"] = pd.to_datetime(
        episodes["DEC"], format="%d/%m/%Y", errors="coerce"
    )

    over_17_days = episodes["DEC"] > episodes["DECOM"] + pd.DateOffset(days=17)
    error_mask = (episodes["LS"] == "V3") & over_17_days

    return {"Episodes": episodes.index[error_mask].to_list()}


def test_validate():
    import pandas as pd

    test_eps = pd.DataFrame(
        [
            {
                "CHILD": 101,
                "DECOM": "01/01/2000",
                "DEC": "01/01/2001",
                "LS": "V3",
            },  # 0 Fail!
            {"CHILD": 101, "DECOM": "01/01/2001", "DEC": "20/12/2001", "LS": "X"},  # 1
            {
                "CHILD": 101,
                "DECOM": "20/12/2001",
                "DEC": "12/01/2002",
                "LS": "V3",
            },  # 2 Fail!
            {
                "CHILD": 2002,
                "DECOM": "01/01/2000",
                "DEC": "10/01/2000",
                "LS": "V3",
            },  # 3
            {"CHILD": 2002, "DECOM": "10/01/2000", "DEC": "23/01/2001", "LS": "X"},  # 4
            {
                "CHILD": 2002,
                "DECOM": "01/01/2002",
                "DEC": "18/01/2002",
                "LS": "V3",
            },  # 5 pass -17 days
            {
                "CHILD": 2002,
                "DECOM": "01/02/2002",
                "DEC": "19/02/2002",
                "LS": "V3",
            },  # 6 Fail! - 18 days
            {
                "CHILD": 2002,
                "DECOM": "11/01/2002",
                "DEC": "25/01/2002",
                "LS": "J2",
            },  # 7
            {"CHILD": 30003, "DECOM": "25/01/2002", "DEC": "10/03/2001", "LS": "J2"},
            # 8 pass - bigger problems: DEC < DECOM
            {
                "CHILD": 30003,
                "DECOM": "25/01/2002",
                "DEC": pd.NA,
                "LS": "V3",
            },  # 9 Fail! (DEC.isna --> collection_end )
            {
                "CHILD": 30003,
                "DECOM": pd.NA,
                "DEC": "25/01/2002",
                "LS": "V3",
            },  # 10 pass - bigger problems: no DECOM
            {
                "CHILD": 30003,
                "DECOM": pd.NA,
                "DEC": pd.NA,
                "LS": "V3",
            },  # 11 pass - bigger problems: no dates
        ]
    )

    test_meta = {"collection_end": "01/04/2002"}

    test_dfs = {"Episodes": test_eps, "metadata": test_meta}

    result = validate(test_dfs)

    assert result == {"Episodes": [0, 2, 6, 9]}
