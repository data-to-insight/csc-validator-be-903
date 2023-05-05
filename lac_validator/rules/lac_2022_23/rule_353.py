import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="353",
    message="No episode submitted can start before 14 October 1991.",
    affected_fields=["DECOM"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]
        epi["DECOM"] = pd.todatetime(epi["DECOM"], format="%d/%m/%Y", errors="coerce")
        mindecomallowed = pd.todatetime(
            "14/10/1991", format="%d/%m/%Y", errors="coerce"
        )
        errormask = epi["DECOM"] < mindecomallowed
        return {"Episodes": epi.index[errormask].tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {"DECOM": pd.NA},  # 0
            {"DECOM": "02/06/1980"},  # 1   Fails
            {"DECOM": "06/06/1890"},  # 2   Fails
            {"DECOM": "08/06/2020"},  # 3
        ]
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [1, 2]}
