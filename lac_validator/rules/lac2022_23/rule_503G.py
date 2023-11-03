import pandas as pd

from lac_validator.fixtures import current_episodes, previous_episodes
from lac_validator.rule_engine import rule_definition
from lac_validator.rules.rule_utils import compare_placement_coordinates


@rule_definition(
    code="503G",
    message="The distance in first episode does not match open episode at end of last year.",
    affected_fields=["PL_DISTANCE"],
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

        this_one = field
        pre_one = this_one + "_PRE"

        # if subval == 'G':
        err_mask = (
            abs(
                merged_co[this_one].astype(float, errors="ignore")
                - merged_co[pre_one].astype(float, errors="ignore")
            )
            >= 0.2
        ) | (
            merged_co[pre_one].isna() & merged_co[this_one].notna()
            | (merged_co[pre_one].isna() & merged_co[this_one].notna())
        )

        err_mask = err_mask & merged_co["DEC_PRE"].isna()

        err_list = merged_co["index"][err_mask].unique().tolist()
        err_list.sort()
        return {"Episodes": err_list}


def test_validate():
    fake_epi = current_episodes.copy()
    fake_epi_last = previous_episodes.copy()

    fake_dfs = {"Episodes": fake_epi, "Episodes_last": fake_epi_last}

    result = validate(fake_dfs)

    assert result == {"Episodes": [4, 6]}
