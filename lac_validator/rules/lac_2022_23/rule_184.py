import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="184",
    message="Date of decision that a child should be placed for adoption is before the child was born.",
    affected_fields=["DATE_PLACED", "DOB"],  # PlacedAdoptino  # Header
)
def validate(dfs):
    if "Header" not in dfs or "PlacedAdoption" not in dfs:
        return {}
    else:
        childrecord = dfs["Header"]
        placedforadoption = dfs["PlacedAdoption"]

        alldata = placedforadoption.resetindex().merge(
            childrecord, how="left", on="CHILD", suffixes=[None, "P4A"]
        )

        alldata["DATEPLACED"] = pd.todatetime(
            alldata["DATEPLACED"], format="%d/%m/%Y", errors="coerce"
        )
        alldata["DOB"] = pd.todatetime(
            alldata["DOB"], format="%d/%m/%Y", errors="coerce"
        )

        mask = (alldata["DATEPLACED"] >= alldata["DOB"]) | alldata["DATEPLACED"].isna()

        validationerror = ~mask

        validationerrorlocations = alldata[validationerror]["index"].unique()

        return {"PlacedAdoption": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data_header = pd.DataFrame(
        {
            "CHILD": ["111", "112", "113", "114"],
            "DOB": ["01/10/2017", "31/05/2018", "10/03/2019", "19/08/2020"],
        }
    )
    fake_data_placed = pd.DataFrame(
        {
            "CHILD": ["111", "112", "113", "114"],
            "DATE_PLACED": ["01/10/2017", "10/02/2019", "10/02/2019", pd.NA],
        }
    )

    fake_dfs = {"Header": fake_data_header, "PlacedAdoption": fake_data_placed}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"PlacedAdoption": [2]}
