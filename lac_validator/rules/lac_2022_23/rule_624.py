from validator903.types import ErrorDefinition


@rule_definition(
    code="624",
    message="Date of birth of the first child contradicts the date of birth of the first child previously "
    + "recorded.",
    affected_fields=["MC_DOB"],
)
def validate(dfs):
    if "Header" not in dfs or "Headerlast" not in dfs:
        return {}
    else:
        hea = dfs["Header"]
        heapre = dfs["Headerlast"]
        hea["origidx"] = hea.index

        errco = hea.merge(heapre, how="inner", on="CHILD", suffixes=["", "PRE"]).query(
            "MCDOBPRE.notna() & (MCDOB != MCDOBPRE)"
        )

        errlist = errco["origidx"].unique().tolist()
        errlist.sort()
        return {"Header": errlist}


def test_validate():
    import pandas as pd

    hdr = pd.DataFrame(
        [
            {"CHILD": "111", "MC_DOB": "01/06/2020"},  # 0
            {"CHILD": "222", "MC_DOB": "04/06/2020"},  # 1
            {"CHILD": "333", "MC_DOB": pd.NA},  # 2
            {"CHILD": "444", "MC_DOB": "08/09/2020"},  # 3
            {"CHILD": "555", "MC_DOB": pd.NA},  # 4
            {"CHILD": "66", "MC_DOB": "01/02/2020"},  # 5
        ]
    )
    hdr_last = pd.DataFrame(
        [
            {"CHILD": "111", "MC_DOB": "01/06/2020"},  # 0
            {"CHILD": "222", "MC_DOB": "04/06/2020"},  # 1
            {"CHILD": "333", "MC_DOB": "01/06/2019"},  # 2
            {"CHILD": "444", "MC_DOB": "10/09/2020"},  # 3
            {"CHILD": "555", "MC_DOB": pd.NA},  # 4
            {"CHILD": "66", "MC_DOB": pd.NA},  # 5
        ]
    )
    fake_dfs = {"Header": hdr, "Header_last": hdr_last}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Header": [2, 3]}
