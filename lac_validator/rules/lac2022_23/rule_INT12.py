import pandas as pd

from lac_validator.fixtures import fake_INT_file, fake_INT_header
from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="INT12",
    message="Internal Check: DOB in PlacedAdoption is different to DOB in Header.",
    affected_fields=["DOB"],
    tables=["Header", "PlacedAdoption"],
)
def validate(dfs):
    if "Header" not in dfs or "PlacedAdoption" not in dfs:
        return {}
    else:
        header = dfs["Header"]
        file = dfs["PlacedAdoption"]

        header["DOB"] = pd.to_datetime(
            header["DOB"], format="%d/%m/%Y", errors="coerce"
        )
        file["DOB"] = pd.to_datetime(file["DOB"], format="%d/%m/%Y", errors="coerce")

        file["index_file"] = file.index

        merged = header.merge(
            file[["CHILD", "DOB", "index_file"]],
            on="CHILD",
            indicator=True,
            how="right",
            suffixes=["_header", "_file"],
        )

        mask = (
            (merged["DOB_header"] != merged["DOB_file"])
            & (merged["DOB_header"].notna() & merged["DOB_file"].notna())
            & (merged["_merge"] != "right_only")
        )
        eps_error_locations = merged.loc[mask, "index_file"]
        return {"PlacedAdoption": eps_error_locations.unique().tolist()}


def test_validate():
    fake_dfs = {
        "Header": fake_INT_header.copy(),
        "PlacedAdoption": fake_INT_file.copy(),
    }
    result = validate(fake_dfs)
    assert result == {"PlacedAdoption": [2]}
