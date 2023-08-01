from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="378",
    message="A child who is placed with parent(s) cannot be looked after under a single period of accommodation under Section 20 of the Children Act 1989.",
    affected_fields=["PLACE", "LS"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        # the & sign supercedes the ==, so brackets are necessary here
        mask = (episodes["PLACE"] == "P1") & (episodes["LS"] == "V2")
        error_locations = episodes.index[mask]
        return {"Episodes": error_locations.to_list()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {"CHILD": "11", "PLACE": "P1", "LS": "x", "REC": "x"},  # 0
            {"CHILD": "202", "PLACE": "x", "LS": "D1", "REC": "x"},  # 1
            {"CHILD": "3003", "PLACE": "A4", "LS": "D1", "REC": "E12"},  # 2
            {"CHILD": "40004", "PLACE": "P1", "LS": "V2", "REC": "E12"},  # 3
            {"CHILD": "5005", "PLACE": "A5", "LS": "x", "REC": "x"},  # 4
            {"CHILD": "606", "PLACE": "A6", "LS": "V2", "REC": "x"},  # 5
            {"CHILD": "77", "PLACE": "x", "LS": "x", "REC": "x"},  # 6
        ]
    )
    fake_dfs = {"Episodes": fake_data}
    
    result = validate(fake_dfs)
    assert result == {"Episodes": [3]}
