import pandas as pd

from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="626",
        description="Child was reported as a mother but the date of birth of the first child is before the current "
        + "year which contradicts with the mother status recorded last year.",
        affected_fields=["MOTHER", "MC_DOB"],
    )

    def _validate(dfs):
        if "Header" not in dfs or "Header_last" not in dfs:
            return {}
        else:
            header = dfs["Header"]
            header_prev = dfs["Header_last"]
            collection_start = dfs["metadata"]["collection_start"]
            header["MC_DOB"] = pd.to_datetime(
                header["MC_DOB"], format="%d/%m/%Y", errors="coerce"
            )
            collection_start = pd.to_datetime(
                collection_start, format="%d/%m/%Y", errors="coerce"
            )
            header["orig_idx"] = header.index
            header = header.query("MC_DOB.notna()")
            merged = header.merge(
                header_prev, how="inner", on="CHILD", suffixes=["", "_PRE"]
            )
            merged["MOTHER"] = pd.to_numeric(merged["MOTHER"], errors="coerce")
            merged["MOTHER_PRE"] = pd.to_numeric(merged["MOTHER_PRE"], errors="coerce")
            err_co = merged[
                (merged["MOTHER"] == 1)
                & (merged["MOTHER_PRE"] == 0)
                & (merged["MC_DOB"] < collection_start)
            ]
            err_list = err_co["orig_idx"].unique().tolist()
            err_list.sort()
            return {"Header": err_list}

    return error, _validate


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
