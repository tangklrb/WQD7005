Original data set: 68769 rows * 102 cols

In general, the following steps are taken part:
1. Drop unhelpful columns
2. Fill NA for categorial columns (most of them has category for Unknown)
3. Drop rows with missing values in important columns
4. Drop rows which are not single property listing
5. Cleaning/Correcting are heavily done on columns for Built Up Area and Land Area due to the complexity of possible values
6. Convert Built Up Area and Land Area to use a standard unit of measurement (square feet)
7. Create new column such as price psf, which helpful to identify outliers
8. Fill missing Geo Coordiates by integrating another dataset
9. Removed outliers and rows which still has missing important data

Cleaned data set: 46139 rows * 26 cols
