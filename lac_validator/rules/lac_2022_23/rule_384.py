from validator903.types import ErrorDefinition


@rule_definition(
    code="384",
    message="A child receiving respite care cannot be in a long-term foster placement ",
    affected_fields=["PLACE", "LS"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        # Where <LS> = 'V3' or 'V4' then <PL> must not be 'U1' or 'U4'
        mask = ((episodes["LS"] == "V3") | (episodes["LS"] == "V4")) & (
            (episodes["PLACE"] == "U1") | (episodes["PLACE"] == "U4")
        )
        errorlocations = episodes.index[mask]
        return {"Episodes": errorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {
                "CHILD": "11",
                "PLACE": "U1",
                "LS": "V4",
            },  # 0
            {
                "CHILD": "202",
                "PLACE": "x",
                "LS": "D1",
            },  # 1
            {
                "CHILD": "3003",
                "PLACE": "U4",
                "LS": "V3",
            },  # 2
            {
                "CHILD": "40004",
                "PLACE": "P1",
                "LS": "V3",
            },  # 3
            {
                "CHILD": "5005",
                "PLACE": "A5",
                "LS": "x",
            },  # 4
            {
                "CHILD": "606",
                "PLACE": "A6",
                "LS": "V4",
            },  # 5
            {"CHILD": "77", "PLACE": "x", "LS": "x"},  # 6
        ]
    )
    fake_dfs = {"Episodes": fake_data}
    error_defn, error_func = validate()
    result = error_func(fake_dfs)
    assert result == {"Episodes": [0, 2]}
