import pandas as pd
import pytest

from lac_validator.rule_engine import RuleDefinition
from lac_validator.rules.ruleset_utils import get_year_ruleset
from lac_validator.utils import (
    add_col_to_episodes_CONTINUOUSLY_LOOKED_AFTER,
    add_col_to_tables_CONTINUOUSLY_LOOKED_AFTER,
)


def test_get_year_ruleset():
    registry = get_year_ruleset("2025")

    assert len(registry) == 305

    assert isinstance(registry, dict)
    assert isinstance(list(registry.values())[1], RuleDefinition)


def test_add_col_to_episodes_CONTINUOUSLY_LOOKED_AFTER():
    collection_start = "01/04/1980"
    collection_end = "31/03/1981"

    eps = pd.DataFrame(
        [
            {
                "CHILD": "1",
                "DECOM": "01/03/1980",
                "DEC": "31/03/1981",
                "LS": "o",
                "REC": "X1",
                "RNE": "o",
            },
            {
                "CHILD": "2",
                "DECOM": "01/03/1980",
                "DEC": "30/03/1981",
                "LS": "o",
                "REC": "X1",
                "RNE": "o",
            },
            {
                "CHILD": "3",
                "DECOM": "01/03/1980",
                "DEC": "01/01/1981",
                "LS": "V3",
                "REC": "X1",
                "RNE": "o",
            },  # False
            {
                "CHILD": "4",
                "DECOM": "01/02/1970",
                "DEC": pd.NA,
                "LS": "o",
                "REC": "!!",
                "RNE": "o",
            },
            {
                "CHILD": "5555",
                "DECOM": "01/03/1979",
                "DEC": "01/01/1981",
                "LS": "o",
                "REC": "X1",
                "RNE": "o",
            },
            {
                "CHILD": "5555",
                "DECOM": "01/01/1981",
                "DEC": pd.NA,
                "LS": "o",
                "REC": pd.NA,
                "RNE": "o",
            },
            {
                "CHILD": "6",
                "DECOM": "01/03/1979",
                "DEC": "01/01/1981",
                "LS": "o",
                "REC": "!!",
                "RNE": "o",
            },  # !! - False
            {
                "CHILD": "6",
                "DECOM": "01/01/1981",
                "DEC": pd.NA,
                "LS": "o",
                "REC": pd.NA,
                "RNE": "o",
            },  # False
            {
                "CHILD": "7777",
                "DECOM": "01/03/1979",
                "DEC": "01/01/1981",
                "LS": "o",
                "REC": "X1",
                "RNE": "o",
            },  # False
            {
                "CHILD": "7777",
                "DECOM": "01/01/1981",
                "DEC": "01/07/1981",
                "LS": "o",
                "REC": "o",
                "RNE": "S",
            },  # !! - False
            {
                "CHILD": "8",
                "DECOM": "01/01/1981",
                "DEC": "31/03/1999",
                "LS": "o",
                "REC": "o",
                "RNE": "S",
            },  # False
            {
                "CHILD": "999",
                "DECOM": "01/03/1970",
                "DEC": "31/03/1975",
                "LS": "o",
                "REC": "X1",
                "RNE": "o",
            },  # not in year
            {
                "CHILD": "999",
                "DECOM": "01/03/1980",
                "DEC": "31/03/1985",
                "LS": "o",
                "REC": "X1",
                "RNE": "o",
            },  # throughout
            {
                "CHILD": "909090",
                "DECOM": "01/03/1970",
                "DEC": "31/03/1975",
                "LS": "o",
                "REC": "X1",
                "RNE": "S",
            },  # not in yr
        ]
    )
    eps = add_col_to_episodes_CONTINUOUSLY_LOOKED_AFTER(
        eps, collection_start, collection_end
    )

    assert eps["CONTINUOUSLY_LOOKED_AFTER"].to_list() == [
        True,
        True,
        False,
        True,
        True,
        True,
        False,
        False,
        False,
        False,
        False,
        True,
        True,
        False,
    ]


def test_add_col_to_tables_CONTINUOUSLY_LOOKED_AFTER():
    collection_start = "01/04/1980"
    collection_end = "31/03/1981"

    eps = pd.DataFrame(
        [
            {
                "CHILD": "1",
                "DECOM": "01/03/1980",
                "DEC": "31/03/1981",
                "LS": "o",
                "REC": "X1",
                "RNE": "o",
            },
            {
                "CHILD": "2",
                "DECOM": "01/03/1980",
                "DEC": "30/03/1981",
                "LS": "o",
                "REC": "X1",
                "RNE": "o",
            },
            {
                "CHILD": "3",
                "DECOM": "01/03/1980",
                "DEC": "01/01/1981",
                "LS": "V3",
                "REC": "X1",
                "RNE": "o",
            },  # !!- False
            {
                "CHILD": "4",
                "DECOM": "01/02/1970",
                "DEC": pd.NA,
                "LS": "o",
                "REC": "!!",
                "RNE": "o",
            },
            {
                "CHILD": "5555",
                "DECOM": "01/03/1979",
                "DEC": "01/01/1981",
                "LS": "o",
                "REC": "X1",
                "RNE": "o",
            },
            {
                "CHILD": "5555",
                "DECOM": "01/01/1981",
                "DEC": pd.NA,
                "LS": "o",
                "REC": pd.NA,
                "RNE": "o",
            },
            {
                "CHILD": "6",
                "DECOM": "01/03/1979",
                "DEC": "01/01/1981",
                "LS": "o",
                "REC": "!!",
                "RNE": "o",
            },  # !! - False
            {
                "CHILD": "6",
                "DECOM": "01/01/1981",
                "DEC": pd.NA,
                "LS": "o",
                "REC": pd.NA,
                "RNE": "o",
            },  # False
            {
                "CHILD": "7777",
                "DECOM": "01/03/1979",
                "DEC": "01/01/1981",
                "LS": "o",
                "REC": "X1",
                "RNE": "o",
            },  # False
            {
                "CHILD": "7777",
                "DECOM": "01/01/1981",
                "DEC": "01/07/1981",
                "LS": "o",
                "REC": "o",
                "RNE": "S",
            },  # !! - False
            {
                "CHILD": "8",
                "DECOM": "01/01/1981",
                "DEC": "31/03/1999",
                "LS": "o",
                "REC": "o",
                "RNE": "S",
            },  # !! - False
            {
                "CHILD": "303",
                "DECOM": "01/03/1970",
                "DEC": "31/03/1975",
                "LS": "o",
                "REC": "X1",
                "RNE": "o",
            },  # not in year
            {
                "CHILD": "303",
                "DECOM": "01/03/1980",
                "DEC": "31/03/1985",
                "LS": "o",
                "REC": "X1",
                "RNE": "o",
            },  # throughout
            {
                "CHILD": "404040",
                "DECOM": "01/03/1970",
                "DEC": "31/03/1975",
                "LS": "o",
                "REC": "X1",
                "RNE": "S",
            },  # not in yr
        ]
    )

    header = pd.DataFrame(
        {"CHILD": ["1", "2", "3", "4", "5555", "6", "7777", "99999999", "404040"]}
    )

    oc3 = pd.DataFrame(
        {
            "CHILD": ["999999", "1", "2", "3", "9999", "8", "303", "404040"],
            "blahh": ["blahhh", "x", "y", "z", "dfds", "q", "xxx", "yyyyyy"],
        }
    )

    missing = pd.DataFrame(
        {
            "CHILD": ["999999", "1", "1", "1", "2", "3", "9999", "8", "303"],
            "blahh": ["blahhh", "x", "y", "z", "y", "z", "dfds", "q", "xyz"],
        }
    )

    dfs = {
        "Episodes": eps,
        "Header": header,
        "Missing": missing,
        "OC3": oc3,
        "metadata": {
            "collection_start": collection_start,
            "collection_end": collection_end,
        },
    }

    # Test with multiple tables
    header, missing, oc3 = add_col_to_tables_CONTINUOUSLY_LOOKED_AFTER(
        dfs, ["Header", "Missing", "OC3"]
    )

    assert header["CONTINUOUSLY_LOOKED_AFTER"].to_list() == [
        True,
        True,
        False,
        True,
        True,
        False,
        False,
        False,
        False,
    ]
    assert missing["CONTINUOUSLY_LOOKED_AFTER"].to_list() == [
        False,
        True,
        True,
        True,
        True,
        False,
        False,
        False,
        True,
    ]
    assert oc3["CONTINUOUSLY_LOOKED_AFTER"].to_list() == [
        False,
        True,
        True,
        False,
        False,
        False,
        True,
        False,
    ]

    # Test with single tables
    missing = add_col_to_tables_CONTINUOUSLY_LOOKED_AFTER(dfs, "Missing")
    assert missing["CONTINUOUSLY_LOOKED_AFTER"].to_list() == [
        False,
        True,
        True,
        True,
        True,
        False,
        False,
        False,
        True,
    ]

    episodes = add_col_to_tables_CONTINUOUSLY_LOOKED_AFTER(dfs, "Episodes")
    assert eps["CONTINUOUSLY_LOOKED_AFTER"].to_list() == [
        True,
        True,
        False,
        True,
        True,
        True,
        False,
        False,
        False,
        False,
        False,
        True,
        True,
        False,
    ]

    # Test with bad table names:
    with pytest.raises(KeyError):
        add_col_to_tables_CONTINUOUSLY_LOOKED_AFTER(dfs, ["Header", "WHOOPS"])
    with pytest.raises(KeyError):
        add_col_to_tables_CONTINUOUSLY_LOOKED_AFTER(dfs, "WHOOPS")
    with pytest.raises(ValueError):
        add_col_to_tables_CONTINUOUSLY_LOOKED_AFTER(dfs, "metadata")

    # Test without episodes
    del dfs["Episodes"]
    with pytest.raises(KeyError):
        add_col_to_tables_CONTINUOUSLY_LOOKED_AFTER(dfs, ["Episodes", "Missing"])
