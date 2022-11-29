import pandas as pd

#episodes = pd.read_csv('/workspaces/quality-lac-data-beta-validator/tests/fake_data/episodes.csv')
#placedAdoptions = pd.read_csv('/workspaces/quality-lac-data-beta-validator/tests/fake_data/placed_for_adoption.csv')

episodes = pd.DataFrame({
    'CHILD': ['0', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', ],
    'REC': ['x', 'E11', 'E12', 'E11', 'E12', 'E11', 'E12', 'E11', 'E11', 'E12', ],
})
placedAdoptions = pd.DataFrame({
    'CHILD': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'D', 'E', 'I', 'I', 'I'],
    'DATE_PLACED_CEASED': [pd.NA, pd.NA, pd.NA, '01/01/2020', '01/01/2020', '15/04/2020', pd.NA, '28th Jan 1930', '02/01/2020', '01/01/1930', '01/01/1930', '02/01/1930',pd.NA],
})

episodes = episodes.reset_index()


rec_codes = ['E11', 'E12']

placeEpisodes = episodes[episodes['REC'].isin(rec_codes)]

merged = placeEpisodes.merge(placedAdoptions, how='left', on='CHILD').set_index('index')
merged['YEAR'] = pd.DatetimeIndex(merged['DATE_PLACED_CEASED'], dayfirst=True).year

episodes_not_null = merged
#episodes_not_null = merged[merged['DATE_PLACED_CEASED'].notnull()]

episodes_not_null['COUNT'] = episodes_not_null.groupby(['CHILD', 'YEAR'], group_keys=False)['DATE_PLACED_CEASED'].transform('count')
#episodes_not_null = episodes_not_null.loc[episodes_not_null.groupby(['DATE_PLACED_CEASED', 'YEAR'], group_keys=False)['CHILD'].count()]
more2 = episodes_not_null[episodes_not_null['COUNT'] > 1]
more2 = more2.drop_duplicates(subset=['CHILD', 'YEAR', 'COUNT'])
print(episodes_not_null)
print(more2)