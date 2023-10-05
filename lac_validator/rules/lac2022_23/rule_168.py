import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="168",
    message="Unique Pupil Number (UPN) is not valid. If unknown, default codes should be UN1, UN2, UN3, UN4 or UN5.",
    affected_fields=["UPN"],
)
def validate(dfs):
    if "Header" not in dfs:
        return {}
    else:
        df = dfs["Header"]
        mask = df["UPN"].str.match(
            r"(^((?![IOS])[A-Z]){1}(\d{12}|\d{11}[A-Z]{1})$)|^(UN[1-5])$", na=False
        )
        mask = ~mask & df["UPN"].notnull()
        return {"Header": df.index[mask].tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "UPN": [
                "UN3",
                "E07295962325C1556",
                "UN5",
                "UN7",
                "UPN3sDSG",
                "X06805040829A",
                "5035247309594",
                pd.NA,
                "L086819786126",
                "K06014812931",
                "J000947841350156",
                "M0940709",
                "I072272729588",
                "N075491517151",
                "Z041674136429",
                "E043016488226",
                "S074885779408",
            ],
        }
    )

    fake_dfs = {"Header": fake_data}

    result = validate(fake_dfs)

    assert result == {"Header": [1, 3, 4, 6, 9, 10, 11, 12, 16]}
