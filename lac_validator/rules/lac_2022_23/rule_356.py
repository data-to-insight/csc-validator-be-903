import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="356",
    message="The date the episode ceased is before the date the same episode started.",
    affected_fields=["DECOM"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        episodes["DECOM"] = pd.todatetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        episodes["DEC"] = pd.todatetime(
            episodes["DEC"], format="%d/%m/%Y", errors="coerce"
        )

        errormask = episodes["DEC"].notna() & (episodes["DEC"] < episodes["DECOM"])

        return {"Episodes": episodes.index[errormask].tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "DECOM": ["14/03/2021", "16/06/2019", "03/10/2020", "07/09/2021"],
            "DEC": ["08/12/2020", "24/08/2021", pd.NA, "07/09/2021"],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [0]}
