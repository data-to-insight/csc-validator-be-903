import pandas as pd


def decom_before_dob(dfs, p_code, y_gap):
    epi = dfs["Episodes"]
    hea = dfs["Header"]

    hea["DOB"] = pd.to_datetime(hea["DOB"], format="%d/%m/%Y", errors="coerce")
    epi["DECOM"] = pd.to_datetime(epi["DECOM"], format="%d/%m/%Y", errors="coerce")
    epi["DEC"] = pd.to_datetime(epi["DEC"], format="%d/%m/%Y", errors="coerce")

    epi.reset_index(inplace=True)
    epi_p2 = epi[epi["PLACE"] == p_code]
    merged_e = epi_p2.merge(hea, how="inner", on="CHILD")
    merged_e = merged_e.dropna(subset=["DECOM", "DEC", "DOB"])
    error_mask = merged_e["DECOM"] < (
        merged_e["DOB"] + pd.offsets.DateOffset(years=y_gap)
    )
    return {"Episodes": merged_e["index"][error_mask].unique().tolist()}


def dec_after_decom(dfs, p_code, y_gap):
    epi = dfs["Episodes"]
    hea = dfs["Header"]

    hea["DOB"] = pd.to_datetime(hea["DOB"], format="%d/%m/%Y", errors="coerce")
    epi["DECOM"] = pd.to_datetime(epi["DECOM"], format="%d/%m/%Y", errors="coerce")
    epi["DEC"] = pd.to_datetime(epi["DEC"], format="%d/%m/%Y", errors="coerce")

    epi.reset_index(inplace=True)
    epi_p2 = epi[epi["PLACE"] == p_code]
    merged_e = epi_p2.merge(hea, how="inner", on="CHILD")
    merged_e = merged_e.dropna(subset=["DECOM", "DEC", "DOB"])
    error_mask = merged_e["DEC"] > (
        merged_e["DECOM"] + pd.offsets.DateOffset(days=y_gap)
    )
    return {"Episodes": merged_e["index"][error_mask].unique().tolist()}


def field_different_from_previous(dfs, field):
    if "Episodes" not in dfs or "Episodes_last" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]
        epi_last = dfs["Episodes_last"]

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

        err_mask = merged_co[this_one].astype(str) != merged_co[pre_one].astype(str)
        err_mask = err_mask & merged_co["DEC_PRE"].isna()

        err_list = merged_co["index"][err_mask].unique().tolist()
        err_list.sort()
        return {"Episodes": err_list}
