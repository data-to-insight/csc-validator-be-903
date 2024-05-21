import pandas as pd

from lac_validator.fixtures import current_episodes, previous_episodes
from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="503G",
    message="The distance in first episode does not match open episode at end of last year.",
    affected_fields=["PL_DISTANCE"],
    tables=["Episodes"],
)
def validate(dfs):
    if "Episodes" not in dfs or "Episodes_last" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]
        epi_last = dfs["Episodes_last"]
        field = "PL_DISTANCE"

        epi["DECOM"] = pd.to_datetime(epi["DECOM"], format="%d/%m/%Y", errors="coerce")
        epi_last["DECOM"] = pd.to_datetime(
            epi_last["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        epi_last["DEC"] = pd.to_datetime(
            epi_last["DEC"], format="%d/%m/%Y", errors="coerce"
        )

        epi.reset_index(inplace=True)

        first_ep_inds = epi.groupby(["CHILD"])["DECOM"].idxmin(skipna=True)
        min_decom = epi.loc[first_ep_inds, :]

        last_ep_inds = epi_last.groupby(["CHILD"])["DECOM"].idxmax(skipna=True)
        max_last_decom = epi_last.loc[last_ep_inds, :]

        merged_co = min_decom.merge(
            max_last_decom, how="inner", on=["CHILD"], suffixes=["", "_PRE"]
        )

        err_mask = (
            abs(
                merged_co["PL_DISTANCE"].astype(float, errors="ignore")
                - merged_co["PL_DISTANCE_PRE"].astype(float, errors="ignore")
            )
            >= 0.2
        ) | (
            merged_co["PL_DISTANCE_PRE"].isna() & merged_co["PL_DISTANCE"].notna()
            | (merged_co["PL_DISTANCE_PRE"].isna() & merged_co["PL_DISTANCE"].notna())
        )

        err_mask = err_mask & merged_co["DEC_PRE"].isna()

        err_list = merged_co["index"][err_mask].unique().tolist()
        err_list.sort()
        return {"Episodes": err_list}


def test_validate():
    fake_epi = current_episodes.copy()
    fake_epi_last = previous_episodes.copy()

    # For the test, this doesn't affect anything except how the data is handled
    # by the field_different function, so it doesn't matter that the years
    # in the test dfs are not accurate to this collection year
    # As seen in conftest collection year is read in as XXXX/XX and stored in metadata
    # as the first four characters using [:4] in _process_metadata in datastore```
    metadata = {"collectionYear": "2022"}

    fake_dfs = {
        "Episodes": fake_epi,
        "Episodes_last": fake_epi_last,
        "metadata": metadata,
    }

    result = validate(fake_dfs)

    assert result == {"Episodes": [4, 6]}
