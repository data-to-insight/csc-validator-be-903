from zipfile import ZIP_BZIP2, ZIP_LZMA, ZipFile

import pandas as pd

print("Reading LA Name <> LA ID mapping...")
la_df = pd.read_csv(
    "scripts/Lower_Tier_Local_Authority_to_Upper_Tier_Local_Authority_(April_2021)_Lookup_in_England_and_Wales.csv",
    usecols=["UTLA21CD", "UTLA21NM"],
)
la_df.columns = ["la_id", "la_name"]  # lower-tier code; upper-tier name
la_df = la_df.sort_values("la_name")
la_df = la_df.drop_duplicates()
la_df.to_json("scripts/la_data.json", orient="records")
print("\tOutput to json done!")

print("Reading main postcodes file...")
df = pd.read_csv(
    "scripts/NSPL_AUG_2021_UK.csv",
    usecols=["pcd", "oseast1m", "osnrth1m", "laua"],
    low_memory=True,
)
df["pcd"] = df.pop("pcd").astype("string").str.replace(" ", "")
df["laua"] = df["laua"].astype("category")

df.drop_duplicates(subset=["pcd"], inplace=True)

df.to_csv("scripts/postcodes.csv")
print("\tCreated CSV, zipping...")
zip_file = ZipFile("scripts/postcodes.zip", "w", compression=ZIP_BZIP2, compresslevel=9)
zip_file.write("scripts/postcodes.csv", arcname="postcodes.csv")
zip_file.close()
print("\tCreated zip file.")

# This is used for testing if needed
df.iloc[:100].to_csv("scripts/postcodes_short.csv")
