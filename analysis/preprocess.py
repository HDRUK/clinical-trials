import pandas as pd

CLINICAL_TRIALS_DATA = pd.read_csv("data/clinical-trials-full.csv")


def select_columns(df):
    selected_col_df = df[
        [
            "A.2 EudraCT number",
            "A.3 Full title of the trial",
            "Trial Status",
            "Date on which this record was first entered in the EudraCT database",
            "B.S1.1.1 Name of Sponsor",
            "E.1.1 Medical condition(s) being investigated",
            "E.1.1.2 Therapeutic area",
            "E.5.1 Primary end point(s)",
            "B.S1.3.1 and B.3.2	Status of the sponsor",
            "D.I1.3.4 Pharmaceutical form",
            "D.I1.2.1.1.2 Name of the Marketing Authorisation holder",
            "D.I1.3.1 Product name",
        ]
    ]
    selected_col_df.reset_index(drop=True, inplace=True)
    
    return selected_col_df


def column_to_upper_case(df, column):
    df[column] = df[column].str.upper()
    return df


def sponsor_column_amendments(df):

    df["B.S1.1.1 Name of Sponsor"] = df["B.S1.1.1 Name of Sponsor"].str.replace(
        "LTD", "LIMITED"
    )
    df["B.S1.1.1 Name of Sponsor"] = df["B.S1.1.1 Name of Sponsor"].str.replace(
        "LIMITED", ""
    )
    df["B.S1.1.1 Name of Sponsor"] = df["B.S1.1.1 Name of Sponsor"].str.replace(
        "&", "AND"
    )
    df["B.S1.1.1 Name of Sponsor"] = df["B.S1.1.1 Name of Sponsor"].str.replace(
        " INC", ""
    )
    
    return df


def string_to_alphanumeric_stripe(df, column):

    df[column] = df[column].str.replace("[^a-zA-Z0-9 ]", "")
    df[column] = df[column].str.strip()

    return df

# TODO: This function is a temporary fix, need to see why 
# it is giving empty rows in extract script
def drop_nan_rows(df):

    df = df.dropna(axis=0, subset=["B.S1.1.1 Name of Sponsor"])
    
    return df


def main():

    clinical_trials_filtered_df = select_columns(CLINICAL_TRIALS_DATA)

    print(len(clinical_trials_filtered_df["B.S1.1.1 Name of Sponsor"].unique()))

    clinical_trials_filtered_df = column_to_upper_case(
        clinical_trials_filtered_df, "B.S1.1.1 Name of Sponsor"
    )
    clinical_trials_filtered_df = sponsor_column_amendments(clinical_trials_filtered_df)
    clinical_trials_filtered_df = string_to_alphanumeric_stripe(
        clinical_trials_filtered_df, "B.S1.1.1 Name of Sponsor"
    )

    clinical_trials_filtered_df = drop_nan_rows(
        clinical_trials_filtered_df)

    print(
        "Length of new unique sponsor list",
        len(clinical_trials_filtered_df["B.S1.1.1 Name of Sponsor"].unique()),
    )


    # Save this dataframe as CSV
    clinical_trials_filtered_df.to_csv(
        "analysis/data/clinical-trails-filtered.csv",
        index=False,
    )


if __name__ == "__main__":
    main()
