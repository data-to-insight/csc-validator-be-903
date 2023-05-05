from validator903.types import ErrorDefinition


@rule_definition(
    code="101",
    message="Gender code is not valid.",
    affected_fields=["SEX"],
)
def validate(dfs):
    if "Header" not in dfs:
        return {}

    header = dfs["Header"]
    codelist = ["1", "2"]

    mask = header["SEX"].astype(str).isin(codelist)

    validationerrormask = ~mask
    validationerrorlocations = header.index[validationerrormask]

    return {"Header": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "SEX": [1, 2, 3, pd.NA],
        }
    )

    fake_dfs = {"Header": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Header": [2, 3]}
