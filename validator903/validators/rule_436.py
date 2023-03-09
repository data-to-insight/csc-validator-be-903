import pandas as pd

from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="436",
        description="Reason for new episode is that both child’s placement and legal status have changed, but this is not reflected in the episode data.",
        affected_fields=["RNE", "LS", "PLACE", "PL_POST", "URN", "PLACE_PROVIDER"],
    )

    def _validate(dfs):
        if "Episodes" not in dfs:
            return {}
        else:
            epi = dfs["Episodes"]
            epi["DECOM"] = pd.to_datetime(
                epi["DECOM"], format="%d/%m/%Y", errors="coerce"
            )

            epi.sort_values(["CHILD", "DECOM"], inplace=True)
            epi.reset_index(inplace=True)
            epi.reset_index(inplace=True)
            epi["LAG_INDEX"] = epi["level_0"].shift(-1)
            epi.fillna(
                value={
                    "LS": "*",
                    "PLACE": "*",
                    "PL_POST": "*",
                    "URN": "*",
                    "PLACE_PROVIDER": "*",
                },
                inplace=True,
            )
            epi_merge = epi.merge(
                epi,
                how="inner",
                left_on="level_0",
                right_on="LAG_INDEX",
                suffixes=["", "_PRE"],
            )

            epi_multi_row = epi_merge[epi_merge["CHILD"] == epi_merge["CHILD_PRE"]]
            epi_has_B_U = epi_multi_row[epi_multi_row["RNE"].isin(["U", "B"])]

            mask_ls = epi_has_B_U["LS"] == epi_has_B_U["LS_PRE"]

            mask1 = epi_has_B_U["PLACE"] == epi_has_B_U["PLACE_PRE"]
            mask2 = epi_has_B_U["PL_POST"] == epi_has_B_U["PL_POST_PRE"]
            mask3 = epi_has_B_U["URN"] == epi_has_B_U["URN_PRE"]
            mask4 = epi_has_B_U["PLACE_PROVIDER"] == epi_has_B_U["PLACE_PROVIDER_PRE"]

            error_mask = mask_ls | (mask1 & mask2 & mask3 & mask4)

            error_list = epi_has_B_U[error_mask]["index"].to_list()
            error_list.sort()
            return {"Episodes": error_list}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {"MISSING": "M", "MIS_END": pd.NA},  # 0
            {"MISSING": pd.NA, "MIS_END": "07/02/2020"},  # 1  Fails
            {"MISSING": "A", "MIS_END": "03/02/2020"},  # 2
            {"MISSING": pd.NA, "MIS_END": pd.NA},  # 3
            {"MISSING": "M", "MIS_END": "01/02/2020"},  # 4
            {"MISSING": pd.NA, "MIS_END": "13/02/2020"},  # 5  Fails
        ]
    )

    fake_dfs = {"Missing": fake_data}

    error_defn, error_func = validate()

    assert error_func(fake_dfs) == {"Missing": [1, 5]}
