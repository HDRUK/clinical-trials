import pandas as pd

df = pd.read_csv('/content/drive/MyDrive/HDRUK/Kabir_Jake_Shared/clinical-trials/clinical trails Tableau/clinical-trials-full.csv')

# Select the columns
selected_col_df = df[['A.2 EudraCT number', 'A.3 Full title of the trial', 'Trial Status','B.S1.1.1 Name of Sponsor', 'E.1.1 Medical condition(s) being investigated', 'E.5.1 Primary end point(s)', "B.S1.3.1 and B.3.2	Status of the sponsor", 'D.I1.3.4 Pharmaceutical form', 'D.I1.2.1.1.2 Name of the Marketing Authorisation holder', 'D.I1.3.1 Product name' ]]
selected_col_df.reset_index(drop=True, inplace=True)

# save this dataframe as CSV
selected_col_df.to_csv('/content/drive/MyDrive/HDRUK/Kabir_Jake_Shared/clinical-trials/clinical trails Tableau/clinical_trails_Tableau.csv',  index=False)
