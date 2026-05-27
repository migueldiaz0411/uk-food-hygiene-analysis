# Manchester Food Hygiene Ratings Data Cleaning


import pandas as pd

file_path = "data/FHRS415en-GB.xml"

df = pd.read_xml(file_path, xpath=".//EstablishmentDetail")


# Analysis
# - Some columns are completely empty and provide no analytical value ✔️
# - Column names use inconsistent casing; convert to snake_case for readability ✔️
# - rating_value column contains both numeric values and text categories - split into separate columns ✔️
# - rating_date is stored as string and needs converting to datetime ✔️
# - post_code column contains full post codes; extract the area code for geographical analysis ✔️
# - Check for duplicates and missing values to ensure data quality ✔️
# - Create a grouping category for rating values 
print("--------------------------------------------- DataFrame head ---------------------------------------------")
print(df.head(10))
print("--------------------------------------------- DataFrame Info ---------------------------------------------")
print(df.info())
print("--------------------------------------------- DataFrame Describe ---------------------------------------------")
print(df.describe())

# checking for duplicates
print(df.duplicated().sum())
df = df.drop_duplicates()
# checking for missing values and dropping unnecessary columns
print(df.isnull().sum())

# dropping empty columns and columns that are not useful for analysis
df = df.drop(columns = ["Scores",
                        "Geocode",
                        "AddressLine1",
                        "AddressLine2",
                        "AddressLine4",
                        "LocalAuthorityName",
                        "LocalAuthorityCode",
                        "LocalAuthorityWebSite",
                        "LocalAuthorityEmailAddress",
                        "SchemeType",
                        "LocalAuthorityBusinessID",
                        "RatingKey",
                        "BusinessTypeID"])
# standardising column names
df = df.rename(columns = {
    "FHRSID" : "fhrs_id",
    "BusinessName" : "business_name",
    "BusinessType" : "business_type",
    "RatingValue" : "rating_value",
    "RatingKey" : "rating_key",
    "RatingDate" : "rating_date",
    "NewRatingPending" : "new_rating_pending",
    "AddressLine3" : "address_line_3",
    "PostCode" : "post_code"
})
# Splitting rating_value column into rating_value_num and rating_value_text

# creating rating_value_num 
df["rating_value_num"] = pd.to_numeric(df["rating_value"], errors = "coerce")
df["rating_value_num"] = df["rating_value_num"].astype("Int64") # using Int64 to allow for NA values in the numeric rating column
# creating rating_value_text
df["rating_value_text"] = df["rating_value"].where(df["rating_value_num"].isna())

# convert rating_date to date format and creating a year and month column

df["rating_date"]  = pd.to_datetime(df["rating_date"], errors = "coerce")
df["rating_year"] = df["rating_date"].dt.year.astype("Int64") # using Int64 to allow for NA values in the year column
df["rating_month"] = df["rating_date"].dt.month.astype("Int64")

# create a post code area column by extracting the first part of the post code
df["postcode_area"] = df["post_code"].str.extract(r"^([A-Z]+[0-9]+)")

#  address_line_3 City names not consitent
df["address_line_3"] = df["address_line_3"].str.strip().str.title()
df["address_line_3"] = df["address_line_3"].replace({
    "Manchestet" : "Manchester",
    "19-25 Piccadilly" : "Piccadilly"
})


# Feature engineering: create a grouping category for rating values

def rating_category(rating):
    if pd.isna(rating):
        return "Unknown"
    elif rating == 5:
        return "Excellent"
    elif rating == 4:
        return "Good"
    elif rating == 3:
        return "Satisfactory"
    elif rating <= 2:
        return "Needs Major Improvement"
    else:
        return "Unknown"
    
df["rating_category"] = df["rating_value_num"].apply(rating_category)

print(df.info())
print(df.head(10))


# exporting cleaned data to a new CSV file
df.to_csv("data/cleaned_manchester_food_hygiene_ratings.csv", index = False)
print("Cleaned data saved to 'data/cleaned_manchester_food_hygiene_ratings.csv'")
