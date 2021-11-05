import pandas as pd

adopt_df = pd.read_csv("placed_for_adoption.csv")
adopt_df.reset_index(inplace = True)
print(len(adopt_df))
adopt_df['DATE_PLACED'] = pd.to_datetime(adopt_df['DATE_PLACED'], format='%d/%m/%Y', errors='coerce')
print(len(adopt_df))


adopt_inds = adopt_df.groupby("CHILD")["DATE_PLACED"].idxmax(skipna=True)
print(len(adopt_inds))

last_decision = adopt_df.loc[adopt_inds]
print(len(last_decision))