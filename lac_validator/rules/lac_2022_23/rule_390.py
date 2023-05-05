from validator903.types import ErrorDefinition


@rule_definition(
    code="390",
    message="Reason episode ceased is adopted but child has not been previously placed for adoption.",
    affected_fields=["PLACE", "REC"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        # If <REC> = 'E11' or 'E12' then <PL> must be one of 'A3', 'A4', 'A5' or 'A6'
        mask = ((episodes["REC"] == "E11") | (episodes["REC"] == "E12")) & ~(
            (episodes["PLACE"] == "A3")
            | (episodes["PLACE"] == "A4")
            | (episodes["PLACE"] == "A5")
            | (episodes["PLACE"] == "A6")
        )
        errorlocations = episodes.index[mask]
        return {"Episodes": errorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {"CHILD": "11", "PLACE": "P1", "LS": "x", "REC": "E11"},  # 0
            {"CHILD": "202", "PLACE": "x", "LS": "D1", "REC": "x"},  # 1
            {"CHILD": "3003", "PLACE": "A4", "LS": "D1", "REC": "E12"},  # 2
            {"CHILD": "40004", "PLACE": "P1", "LS": "V2", "REC": "E12"},  # 3
            {"CHILD": "5005", "PLACE": "A5", "LS": "x", "REC": "E11"},  # 4
            {"CHILD": "606", "PLACE": "A6", "LS": "V2", "REC": "x"},  # 5
            {"CHILD": "77", "PLACE": "x", "LS": "x", "REC": "x"},  # 6
        ]
    )
    fake_dfs = {"Episodes": fake_data}
    error_defn, error_func = validate()
    result = error_func(fake_dfs)
    assert result == {"Episodes": [0, 3]}
