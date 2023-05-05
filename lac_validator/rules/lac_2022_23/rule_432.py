import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="432",
    message="The child ceased to be looked after at the end of the previous episode but the reason for "
    + "the new episode is not started to be looked after.",
    affected_fields=["RNE"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]

        epi["DECOM"] = pd.todatetime(epi["DECOM"], format="%d/%m/%Y", errors="coerce")

        epi.sortvalues(["CHILD", "DECOM"], inplace=True)
        epi.resetindex(inplace=True)
        epi.resetindex(inplace=True)

        recvals1 = ["E2", "E3", "E4A", "E4B", "E5", "E6", "E7", "E8", "E9", "E11"]
        recvals2 = [
            "E12",
            "E13",
            "E14",
            "E15",
            "E16",
            "E17",
            "E41",
            "E45",
            "E46",
            "E47",
            "E48",
        ]
        recvals = recvals1 + recvals2

        epi["LAG"] = epi["level0"].shift(-1)

        errco = epi.merge(
            epi,
            how="inner",
            lefton="level0",
            righton="LAG",
            suffixes=["", "PRE"],
        ).query("CHILD == CHILDPRE & RECPRE.isin(@recvals) & RNE != 'S'")

        errlist = errco["index"].unique().tolist()
        errlist.sort()

        return {"Episodes": errlist}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {"CHILD": "111", "RNE": "P", "DECOM": "01/06/2020", "REC": "E2"},  # 0
            {"CHILD": "111", "RNE": "P", "DECOM": "05/06/2020", "REC": "E3"},  # 1
            {"CHILD": "111", "RNE": "T", "DECOM": "06/06/2020", "REC": "E3"},  # 2
            {"CHILD": "111", "RNE": "S", "DECOM": "08/06/2020", "REC": pd.NA},  # 3
            {"CHILD": "222", "RNE": "S", "DECOM": "05/06/2020", "REC": "E3"},  # 4
            {"CHILD": "333", "RNE": "B", "DECOM": "06/06/2020", "REC": "E3"},  # 5
            {"CHILD": "333", "RNE": "U", "DECOM": "10/06/2020", "REC": pd.NA},  # 6
            {"CHILD": "444", "RNE": "S", "DECOM": "07/06/2020", "REC": "E3"},  # 7
            {"CHILD": "444", "RNE": "S", "DECOM": "08/06/2020", "REC": "E3"},  # 8
            {"CHILD": "444", "RNE": "T", "DECOM": "09/06/2020", "REC": "E3"},  # 9
            {"CHILD": "444", "RNE": "S", "DECOM": "15/06/2020", "REC": "E3"},  # 10
        ]
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [1, 2, 6, 9]}
