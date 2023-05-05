from validator903.types import ErrorDefinition
from validator903.datastore import merge_postcodes


@rule_definition(
    code="392c",
    message="Postcode(s) provided are invalid.",
    affected_fields=["HOME_POST", "PL_POST"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]

        homeprovided = episodes["HOMEPOST"].notna()
        homedetails = mergepostcodes(episodes, "HOMEPOST")
        homevalid = homedetails["pcd"].notna()

        plprovided = episodes["PLPOST"].notna()
        pldetails = mergepostcodes(episodes, "PLPOST")
        plvalid = pldetails["pcd"].notna()

        errormask = (homeprovided & ~homevalid) | (plprovided & ~plvalid)

        return {"Episodes": episodes.index[errormask].tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "HOME_POST": [
                "AB1 0JD",
                "invalid",
                "AB1 0JD",
                "invalid",
                "AB10JD",
            ],
            "PL_POST": [
                "AB1 0JD",
                "AB1 0JD",
                "invalid",
                "invalid",
                "AB1 0JD",
            ],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [1, 2, 3]}
