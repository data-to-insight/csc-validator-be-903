import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="1012",
    message="No other data should be returned for OC3 children who had no episodes in the current year",
    affected_fields=["CHILD"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}

    epi = dfs["Episodes"]

    error_dict = {}
    for table in ["PlacedAdoption", "Missing", "Reviews", "AD1", "PrevPerm", "OC2"]:
        if table in dfs.keys():
            df = dfs[table]
            error_dict[table] = (
                df.reset_index()
                .merge(epi, how="left", on="CHILD", indicator=True)
                .query("_merge == 'left_only'")["index"]
                .unique()
                .tolist()
            )
    return error_dict


def test_validate():
    import pandas as pd

    fake_epi = pd.DataFrame(
        {
            "CHILD": ["111", "222", "333", "444", "555", "555", "666", "666"],
        }
    )
    fake_ado = pd.DataFrame(
        {
            "CHILD": ["777", "222", "333", "444", "555", "666"],
        }
    )  # err at 0
    fake_mis = pd.DataFrame(
        {
            "CHILD": ["111", "888", "333", "444", "555", "666"],
        }
    )  # err at 1
    fake_rev = pd.DataFrame(
        {
            "CHILD": ["111", "222", "999", "444", "555", "666"],
        }
    )  # err at 2
    fake_ad1 = pd.DataFrame(
        {
            "CHILD": ["111", "222", "333", "1010", "555", "666"],
        }
    )  # err at 3
    fake_pre = pd.DataFrame(
        {
            "CHILD": ["111", "222", "333", "444", "1111", "666"],
        }
    )  # err at 4
    fake_oc2 = pd.DataFrame(
        {
            "CHILD": ["111", "222", "333", "444", "555", "1212"],
        }
    )  # err at 5

    fake_dfs = {
        "Episodes": fake_epi,
        "PlacedAdoption": fake_ado,
        "Missing": fake_mis,
        "Reviews": fake_rev,
        "AD1": fake_ad1,
        "PrevPerm": fake_pre,
        "OC2": fake_oc2,
    }

    fake_dfs_partial = {
        "Episodes": fake_epi,
        "AD1": fake_ad1,
        "PrevPerm": fake_pre,
        "OC2": fake_oc2,
    }

    assert validate(fake_dfs) == {
        "PlacedAdoption": [0],
        "Missing": [1],
        "Reviews": [2],
        "AD1": [3],
        "PrevPerm": [4],
        "OC2": [5],
    }

    assert validate(fake_dfs_partial) == {"AD1": [3], "PrevPerm": [4], "OC2": [5]}
