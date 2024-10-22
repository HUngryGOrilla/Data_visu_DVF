import pandas as pd
import streamlit as st

@st.cache_data
def load_data(filepath):
    """
    Load data from a given file path.

    Parameters:
        filepath (str): Path to the data file.

    Returns:
        pd.DataFrame: Loaded DataFrame.
    """
    df = pd.read_csv(filepath, sep='|', decimal=',')
    return df

def select_columns(df, columns):
    """
    Select specific columns from a DataFrame.

    Parameters:
        df (pd.DataFrame): The original DataFrame.
        columns (list): List of columns to select.

    Returns:
        pd.DataFrame: DataFrame with selected columns.
    """
    df = df[columns]
    return df

def add_month_colum(df):
    """
    Add a month column to a DataFrame after converting 'Date mutation' to datetime.

    Parameters:
        df (pd.DataFrame): The DataFrame to process.

    Returns:
        pd.DataFrame: DataFrame with the month column added.
    """
    # Convert 'Date mutation' to datetime format
    df['Date mutation'] = pd.to_datetime(df['Date mutation'], errors='coerce')  # Convert or set invalid parsing to NaT

    # Now extract the month from 'Date mutation'
    df['Month'] = df['Date mutation'].dt.month
    return df

def convert_to_numeric(df, cols):
    """
    Convert specified columns to numeric, coercing errors to NaN.

    Parameters:
        df (pd.DataFrame): The DataFrame to process.
        cols (list): List of column names to convert.

    Returns:
        pd.DataFrame: DataFrame with converted columns.
    """
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def fill_nans(df, value=0):
    """
    Fill NaN values in the DataFrame.

    Parameters:
        df (pd.DataFrame): The DataFrame to process.
        value: Value to replace NaNs with.

    Returns:
        pd.DataFrame: DataFrame with NaNs filled.
    """
    df.fillna(value, inplace=True)
    return df

def drop_duplicates(df):
    """
    Drop duplicate rows from the DataFrame.

    Parameters:
        df (pd.DataFrame): The DataFrame to process.

    Returns:
        pd.DataFrame: DataFrame without duplicates.
    """
    df = df.drop_duplicates()
    return df

def merge_similar_lines(df):
    """
    Merge similar lines by grouping and aggregating.

    Parameters:
        df (pd.DataFrame): The DataFrame to process.

    Returns:
        pd.DataFrame: Merged DataFrame.
    """
    df = df.groupby([
        'Date mutation', 'Nature mutation', 'Valeur fonciere', 'Code departement',
        'Code commune', 'Prefixe de section', 'Section', 'No plan',
        'Surface terrain', 'Nature culture'
    ]).agg({
        'Nombre pieces principales': 'sum',
        'Code type local': 'min',
        'Surface reelle bati': 'sum',
    }).reset_index()
    return df

def remove_outliers(df, column, multiplier=3):
    """
    Remove outliers from a DataFrame column using the IQR method.

    Parameters:
        df (pd.DataFrame): The DataFrame to process.
        column (str): Column name to remove outliers from.
        multiplier (int): Multiplier for the IQR to define bounds.

    Returns:
        pd.DataFrame: DataFrame without outliers in the specified column.
    """
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR
    df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
    return df

def separate_datasets(df):
    """
    Separate the DataFrame into built and land-only properties.

    Parameters:
        df (pd.DataFrame): The DataFrame to separate.

    Returns:
        tuple: (df_built, df_land)
    """
    df_built = df[df["Surface reelle bati"] > 0]
    df_land = df[df["Surface reelle bati"] == 0]
    return df_built, df_land

@st.cache_data
def cleaning(filepath):
    #data = '../data/valeursfoncieres-2022.txt'     does not work if lauched from main
    data =filepath

    # Load the data
    df = load_data(data)

    # Columns to keep
    columns = [
        "No disposition", "Date mutation", "Nature mutation", "Valeur fonciere",
        "Code departement", "Code commune", "Prefixe de section", "Section",
        "No plan", 'No Volume', "Code type local", "Surface reelle bati",
        "Surface terrain", "Nombre pieces principales", "Nature culture"
    ]
    df = select_columns(df, columns)

    # Convert columns to numeric
    cols_to_convert = ['Surface reelle bati', 'Surface terrain']
    df = convert_to_numeric(df, cols_to_convert)

    # Fill NaNs with 0
    df = fill_nans(df, value=0)

    # Drop duplicates
    df = drop_duplicates(df)

    # Merge similar lines
    df = merge_similar_lines(df)

    df = add_month_colum(df)

    # Remove outliers in 'Surface terrain'
    df_process = remove_outliers(df, "Surface terrain", multiplier=3)

    df_process= df_process[df_process["Code type local"] > 0]

    # Separate into built and land-only datasets
    df_built, df_land = separate_datasets(df_process)

    # Remove outliers in 'Surface reelle bati' for built properties
    df_built = remove_outliers(df_built, "Surface reelle bati", multiplier=3)

    # Remove outliers in 'Valeur fonciere' for built properties
    df_built = remove_outliers(df_built, "Valeur fonciere", multiplier=3)

    # Remove outliers in 'Valeur fonciere' for land-only properties
    df_land = remove_outliers(df_land, "Valeur fonciere", multiplier=3)

    return df_built, df_land,df
