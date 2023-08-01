import pandas as pd

fake_INT_header = pd.DataFrame(
    {
        "CHILD": ["101", "102", "103", "104", "101", "102", "103", "104", "106"],
        "DOB": [
            "01/04/2020",
            pd.NA,
            "01/04/2020",
            pd.NA,
            "01/04/2020",
            pd.NA,
            "01/04/2020",
            pd.NA,
            pd.NA,
        ],
        "SEX": ["M", "F", "M", "F", "M", "F", "M", "F", pd.NA],
    }
)

fake_INT_file = pd.DataFrame(
    {
        "CHILD": ["101", "102", "103", "105"],
        "DOB": ["01/04/2020", pd.NA, "04/01/2020", "01/04/2020"],
        "SEX": ["M", "F", "F", "F"],
    }
)


current_episodes = pd.DataFrame(
    [
        {
            "CHILD": "101",
            "RNE": "S",
            "DECOM": "01/04/2020",
            "DEC": "04/06/2020",
            "PL_DISTANCE": 400,
            "PL_LA": "WAL",
        },
        {
            "CHILD": "101",
            "RNE": "P",
            "DECOM": "04/06/2020",
            "DEC": pd.NA,
            "PL_DISTANCE": 400,
            "PL_LA": "WAL",
        },
        {
            "CHILD": "103",
            "RNE": "P",
            "DECOM": "03/03/2020",
            "DEC": "10/07/2020",
            "PL_DISTANCE": 10,
            "PL_LA": "816",
        },
        {
            "CHILD": "103",
            "RNE": "L",
            "DECOM": "10/07/2020",
            "DEC": "09/12/2020",
            "PL_DISTANCE": 10,
            "PL_LA": "816",
        },
        {
            "CHILD": "104",
            "RNE": "B",
            "DECOM": "28/03/2020",
            "DEC": pd.NA,
            "PL_DISTANCE": 185,
            "PL_LA": "356",
        },
        {
            "CHILD": "105",
            "RNE": "L",
            "DECOM": "16/04/2020",
            "DEC": pd.NA,
            "PL_DISTANCE": "165",
            "PL_LA": "112",
        },
        {
            "CHILD": "106",
            "RNE": "S",
            "DECOM": "04/11/2020",
            "DEC": pd.NA,
            "PL_DISTANCE": "165",
            "PL_LA": "112",
        },
    ]
)

previous_episodes = pd.DataFrame(
    [
        {
            "CHILD": "101",
            "RNE": "P",
            "DECOM": "04/06/2020",
            "DEC": "04/06/2021",
            "PL_DISTANCE": 400,
            "PL_LA": "WAL",
        },
        {
            "CHILD": "101",
            "RNE": "P",
            "DECOM": "04/06/2021",
            "DEC": pd.NA,
            "PL_DISTANCE": 400,
            "PL_LA": "WAL",
        },
        {
            "CHILD": "102",
            "RNE": "L",
            "DECOM": "20/12/2020",
            "DEC": "07/04/2021",
            "PL_DISTANCE": 10,
            "PL_LA": "816",
        },
        # Ignore all
        {
            "CHILD": "103",
            "RNE": "L",
            "DECOM": "02/02/2021",
            "DEC": pd.NA,
            "PL_DISTANCE": 10,
            "PL_LA": "816",
        },  # Ignore all
        {
            "CHILD": "104",
            "RNE": "B",
            "DECOM": "28/03/2020",
            "DEC": pd.NA,
            "PL_DISTANCE": 999.9,
            "PL_LA": "CON",
        },  # Fail all
        {
            "CHILD": "105",
            "RNE": "L",
            "DECOM": "16/04/2020",
            "DEC": pd.NA,
            "PL_DISTANCE": 165,
            "PL_LA": 112,
        },
        {
            "CHILD": "106",
            "RNE": "S",
            "DECOM": "04/11/2020",
            "DEC": pd.NA,
            "PL_DISTANCE": pd.NA,
            "PL_LA": pd.NA,
        },
        # Fail 452 and 503G only
    ]
)
