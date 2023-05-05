from validator903.types import ErrorDefinition


@rule_definition(
    code="1012",
    message="No other data should be returned for OC3 children who had no episodes in the current year",
    affected_fields=["CHILD"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}

    epi = dfs["Episodes"]

    errordict = {}
    for table in ["PlacedAdoption", "Missing", "Reviews", "AD1", "PrevPerm", "OC2"]:
        if table in dfs.keys():
            df = dfs[table]
            errordict[table] = (
                df.resetindex()
                .merge(epi, how="left", on="CHILD", indicator=True)
                .query("merge == 'leftonly'")["index"]
                .unique()
                .tolist()
            )
    return errordict


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

    error_defn, error_func = validate()

    assert error_func(fake_dfs) == {
        "PlacedAdoption": [0],
        "Missing": [1],
        "Reviews": [2],
        "AD1": [3],
        "PrevPerm": [4],
        "OC2": [5],
    }

    assert error_func(fake_dfs_partial) == {"AD1": [3], "PrevPerm": [4], "OC2": [5]}
