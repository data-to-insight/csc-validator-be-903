import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="232",
    message="Sex of the child/young person has been reported as unknown.",
    affected_fields=["SEX"],
    tables=["Header"],
)
def validate(dfs):
    # If <UASC_STATUS> = 1 then <DOB> should be > 11 years prior to <COLLECTION_END_DATE>
    if "Header" not in dfs:
        return {}
    else:
        df = dfs["Header"]

        error_df = df[df['SEX'].str.upper() == "U"]

        errors = error_df.index

        return {"Header": errors.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {"SEX":"U"},  # sex U, fails
            {"SEX":"u"},  # sex u fails
            {"SEX":"m"},
            {"SEX":0},
            
        ]
    )  # over 11, uasc, passes

    fake_metadata = {"collection_end": "31/03/2025"}

    fake_dfs = {"Header": fake_data, "metadata": fake_metadata}

    result = validate(fake_dfs)

    assert result == {"Header": [0, 1]}
