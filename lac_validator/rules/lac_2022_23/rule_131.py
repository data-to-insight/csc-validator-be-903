from validator903.types import ErrorDefinition


@rule_definition(
    code="131",
    message="Data entry for being in touch after leaving care is invalid.",
    affected_fields=["IN_TOUCH"],
)
def validate(dfs):
    if "OC3" not in dfs:
        return {}

    careleavers = dfs["OC3"]
    codelist = ["YES", "NO", "DIED", "REFU", "NREQ", "RHOM"]
    mask = careleavers["INTOUCH"].isin(codelist)

    validationerrormask = ~mask
    validationerrorlocations = careleavers.index[validationerrormask]

    return {"OC3": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "IN_TOUCH": ["yes", "YES", 1, "REFUSE", "REFU", "", pd.NA],
        }
    )

    fake_dfs = {"OC3": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"OC3": [0, 2, 3, 5, 6]}
