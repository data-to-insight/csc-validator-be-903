import pandas as pd

from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="453",
        description="Contradiction between placement distance in the last episode of the previous year and in the first episode of the current year.",
        affected_fields=["PL_DISTANCE"],
    )

    def _validate(dfs):
        if "Episodes" not in dfs:
            return {}
        if "Episodes_last" not in dfs:
            return {}
        else:
            episodes = dfs["Episodes"]
            episodes_last = dfs["Episodes_last"]

            episodes["DECOM"] = pd.to_datetime(
                episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
            )
            episodes_last["DECOM"] = pd.to_datetime(
                episodes_last["DECOM"], format="%d/%m/%Y", errors="coerce"
            )
            episodes["PL_DISTANCE"] = pd.to_numeric(
                episodes["PL_DISTANCE"], errors="coerce"
            )
            episodes_last["PL_DISTANCE"] = pd.to_numeric(
                episodes_last["PL_DISTANCE"], errors="coerce"
            )

            # drop rows with missing DECOM before finding idxmin/max, as invalid/missing values can lead to errors
            episodes = episodes.dropna(subset=["DECOM"])
            episodes_last = episodes_last.dropna(subset=["DECOM"])

            episodes_min = episodes.groupby("CHILD")["DECOM"].idxmin()
            episodes_last_max = episodes_last.groupby("CHILD")["DECOM"].idxmax()

            episodes = episodes[episodes.index.isin(episodes_min)]
            episodes_last = episodes_last[episodes_last.index.isin(episodes_last_max)]

            episodes_merged = (
                episodes.reset_index()
                .merge(
                    episodes_last,
                    how="left",
                    on=["CHILD"],
                    suffixes=("", "_last"),
                    indicator=True,
                )
                .set_index("index")
            )

            in_both_years = episodes_merged["_merge"] == "both"
            same_rne = episodes_merged["RNE"] == episodes_merged["RNE_last"]
            last_year_open = episodes_merged["DEC_last"].isna()
            different_pl_dist = (
                abs(
                    episodes_merged["PL_DISTANCE"] - episodes_merged["PL_DISTANCE_last"]
                )
                >= 0.2
            )

            error_mask = in_both_years & same_rne & last_year_open & different_pl_dist

            validation_error_locations = episodes.index[error_mask]

            return {"Episodes": validation_error_locations.tolist()}

    return error, _validate


def test_validate():
    error_defn, error_func = validate()

    result = error_func(fake_dfs__452_453_503G_503H)

    assert result == {"Episodes": [4]}
