import pandas as pd

from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="180",
        description="Data entry for the strengths and difficulties questionnaire (SDQ) score is invalid.",
        affected_fields=["SDQ_SCORE"],
    )

    def _validate(dfs):
        if "OC2" not in dfs:
            return {}
        else:
            oc2 = dfs["OC2"]

            oc2["SDQ_SCORE_num"] = pd.to_numeric(oc2["SDQ_SCORE"], errors="coerce")

            error_mask = oc2["SDQ_SCORE"].notna() & ~oc2["SDQ_SCORE_num"].isin(
                range(41)
            )

            validation_error_locations = oc2.index[error_mask]

            return {"OC2": validation_error_locations.to_list()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "SDQ_SCORE": ["10", 41, "58", 72, "0", 40, 39.5, 20.0, pd.NA, "XX"],
        }
    )

    fake_dfs = {"OC2": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"OC2": [1, 2, 3, 6, 9]}
