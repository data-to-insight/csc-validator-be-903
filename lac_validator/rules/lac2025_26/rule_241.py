import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="241",
    message="LA of placement is not an LA the provider has premises.",
    affected_fields=["URN"],
    tables=["Episodes"],
)
def validate(dfs):
    # If Ofsted URN is provided and not ‘XXXXXXX’ and <PL> = 'K3' then
    # <PL_LA> must equal Ofsted URN lookup <LA code> for that URN. (where there may be more than one LA per provider in the lookup file)

    if "Episodes" not in dfs:
        return {}
    else:
        df = dfs["Episodes"]
        local_authority = dfs["metadata"]["localAuthority"]

        urn_conditions = df[
            (df["URN"].notna()) & (df["URN"] != "XXXXXXX") & (df["PLACE"] == "K3")
        ]

        errors = urn_conditions[urn_conditions["PL_LA"] != local_authority]

        return {"Episodes": errors.index.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {"PLACE": "K3", "URN": "URNURN", "PL_LA": "CORRECT"},
            {"PLACE": "K3", "URN": "URNURN", "PL_LA": "WRONG"},  # Fails
            {"PLACE": "K3", "URN": pd.NA, "PL_LA": "WRONG"},
            {"PLACE": "U1", "URN": "URNURN", "PL_LA": "WRONG"},
            {"PLACE": "K3", "URN": "XXXXXXX", "PL_LA": "WRONG"},
        ]
    )

    metadata = {
        "localAuthority": "CORRECT",
    }

    fake_dfs = {"Episodes": fake_data, "metadata": metadata}

    result = validate(fake_dfs)

    assert result == {"Episodes": [1]}
