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
