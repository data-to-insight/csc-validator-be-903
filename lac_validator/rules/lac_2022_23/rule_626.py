import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="626",
    message="Child was reported as a mother but the date of birth of the first child is before the current "
    + "year which contradicts with the mother status recorded last year.",
    affected_fields=["MOTHER", "MC_DOB"],
)
def validate(dfs):
    if "Header" not in dfs or "Headerlast" not in dfs:
        return {}
    else:
        header = dfs["Header"]
        headerprev = dfs["Headerlast"]
        collectionstart = dfs["metadata"]["collectionstart"]
        header["MCDOB"] = pd.todatetime(
            header["MCDOB"], format="%d/%m/%Y", errors="coerce"
        )
        collectionstart = pd.todatetime(
            collectionstart, format="%d/%m/%Y", errors="coerce"
        )
        header["origidx"] = header.index
        header = header.query("MCDOB.notna()")
        merged = header.merge(headerprev, how="inner", on="CHILD", suffixes=["", "PRE"])
        merged["MOTHER"] = pd.tonumeric(merged["MOTHER"], errors="coerce")
        merged["MOTHERPRE"] = pd.tonumeric(merged["MOTHERPRE"], errors="coerce")
        errco = merged[
            (merged["MOTHER"] == 1)
            & (merged["MOTHERPRE"] == 0)
            & (merged["MCDOB"] < collectionstart)
        ]
        errlist = errco["origidx"].unique().tolist()
        errlist.sort()
        return {"Header": errlist}


def test_validate():
    import pandas as pd

    header = pd.DataFrame(
        [
            {"CHILD": "111", "MOTHER": 1, "MC_DOB": pd.NA},  # 0
            {"CHILD": "222", "MOTHER": "1", "MC_DOB": "04/01/2020"},  # 1 Fail
            {"CHILD": "333", "MOTHER": 0, "MC_DOB": pd.NA},  # 2
            {"CHILD": "444", "MOTHER": 1.0, "MC_DOB": "01/04/2020"},  # 3
        ]
    )
    header_last = pd.DataFrame(
        [
            {"CHILD": "111", "MOTHER": "1"},  # 0
            {"CHILD": "222", "MOTHER": 0.0},  # 1
            {"CHILD": "333", "MOTHER": "1"},  # 2
            {"CHILD": "444", "MOTHER": "0"},  # 3
        ]
    )
    metadata = {"collection_start": "01/04/2020"}

    fake_dfs = {"Header": header, "Header_last": header_last, "metadata": metadata}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Header": [1]}
