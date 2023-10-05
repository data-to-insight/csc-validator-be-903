import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="166",
    message="Date of review is invalid or blank.",
    affected_fields=["REVIEW"],
)
def validate(dfs):
    if "Reviews" not in dfs:
        return {}
    else:
        review = dfs["Reviews"]

        error_mask = pd.to_datetime(
            review["REVIEW"], format="%d/%m/%Y", errors="coerce"
        ).isna()

        validation_error_locations = review.index[error_mask]

        return {"Reviews": validation_error_locations.to_list()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "REVIEW": ["01/01/2021", "19/02/2010", "38/04/2019", "01/01/19", pd.NA],
        }
    )

    fake_dfs = {"Reviews": fake_data}

    result = validate(fake_dfs)

    assert result == {"Reviews": [2, 3, 4]}
