import pandas as pd
from zipfile import ZIP_BZIP2, ZipFile, ZIP_LZMA

print('Reading LA Name <> LA ID mapping...')
la_df = pd.read_csv('scripts/LA_UA names and codes UK as at 04_21.csv', usecols=['LAD21CD','LAD21NM'])
la_df.columns = ['la_id', 'la_name']
la_df = la_df.sort_values('la_name')
la_df.to_json('scripts/la_data.json', orient='records')
print('\tOutput to json!')

print('Reading main postcodes file...')
df = pd.read_csv('scripts/NSPL_MAY_2021_UK.csv', usecols=['pcd', 'lat', 'long', 'laua'], low_memory=True)
df['pcd'] = df.pop('pcd').astype('string')
df['laua'] = df['laua'].astype('category')
df.to_csv('scripts/postcodes.csv')
print('\tCreated CSV, zipping...')
zip_file = ZipFile('scripts/postcodes.zip', 'w', compression=ZIP_BZIP2, compresslevel=9)
zip_file.write('scripts/postcodes.csv', arcname='postcodes.csv')
zip_file.close()
print('\tCreated zip file.')

# This is used for testing if needed
df.iloc[:100].to_csv('scripts/postcodes_short.csv')
