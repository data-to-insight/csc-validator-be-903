import pandas as pd

from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="446",
        description="E1 is not a valid code for episodes starting before December 2005.",
        affected_fields=["LS", "DECOM"],
    )

    def _validate(dfs):
        if "Episodes" not in dfs:
            return {}
        else:
            episodes = dfs["Episodes"]
            episodes["DECOM"] = pd.to_datetime(
                episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
            )
            min_decom_allowed = pd.to_datetime(
                "01/12/2005", format="%d/%m/%Y", errors="coerce"
            )

            mask = episodes["LS"].eq("E1") & (episodes["DECOM"] < min_decom_allowed)
            validation_error_mask = mask
            validation_error_locations = episodes.index[validation_error_mask]

            return {"Episodes": validation_error_locations.tolist()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "LS": ["E1", "E1", "E1", "E1", "E1", "C1"],
            "DECOM": [
                "01/12/2005",
                "15/05/2012",
                pd.NA,
                "20/09/2004",
                "01/10/2005",
                "20/02/2005",
            ],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [3, 4]}
