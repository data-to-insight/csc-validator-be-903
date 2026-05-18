import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="243",
    message="Only placements with providers registered with Ofsted should have a URN reported.",
    affected_fields=["URN"],
    tables=["Episodes"],
)
def validate(dfs):
    # If <PL_LA> in (‘CON’; ‘NIR’ ‘SCO’; ‘WAL’; ‘NUK’) then <URN> should be null
    if "Episodes" not in dfs:
        return {}
    else:
        df = dfs["Episodes"]

        mask = (df["PL_LA"].isin(["CON", "NIR", "SCO", "WAL", "NUK"])) & (
            df["URN"].notna()
        )
        return {"Episodes": df.index[mask].tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {"PL_LA": "H5", "URN": "XXXXXXX"},  # 0
            {"PL_LA": "NIR", "URN": "XXXXXXX"},  # 1 FAILS
            {"PL_LA": "CON", "URN": pd.NA},  # 2
        ]
    )

    fake_dfs = {"Episodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"Episodes": [1]}
