import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="444",
    message="Duplicate UPN has been reported",
    affected_fields=["UPN"],
    tables=["Header"],
)
def validate(dfs):
    # If <UPN> is provided and <UPN> is not in ‘UN1’, ‘UN2’, ‘UN3’, ‘UN4’,’UN5’ then <UPN> must be unique within the LA return in that year.
    if "Header" not in dfs:
        return {}

    df = dfs["Header"]

    no_allowed_duplicates = df[
        ~df["UPN"].isin(["UN1", "UN2", "UN3", "UN4", "UN5"])
    ].copy()

    duplicated_upn_df = no_allowed_duplicates.groupby("UPN").size().to_frame("Count")

    duplicated_upns = (
        duplicated_upn_df[duplicated_upn_df["Count"] > 1].reset_index()["UPN"].to_list()
    )

    has_duplicated_upn = df["UPN"].isin(duplicated_upns)

    validation_error_locations = df.index[has_duplicated_upn]

    return {"Header": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "UPN": [
                "UN1",
                "UN2",
                "UN3",
                "UN4",
                "UN5",
                "UN1",
                "SINGLE1",
                "DUPLICATE1",
                "DUPLICATE1",
                "DUPLICATE2",
                "DUPLICATE2",
            ]
        }
    )

    fake_dfs = {"Header": fake_data}

    result = validate(fake_dfs)

    assert result == {"Header": [7, 8, 9, 10]}
