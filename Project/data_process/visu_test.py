import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dashboard.dataset_cleaning import cleaning
from dashboard.visu_generation import prepare_data_for_plotting, get_numerical_columns, create_plot_options, plot_numerical_distributions


def prepare_data_for_plotting(df, columns_to_plot):
    return df[columns_to_plot]


def get_numerical_columns(df):
    numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns
    return numerical_cols


def create_plot_options(numerical_cols):
    plot_options = {}
    st.sidebar.header("Select plots to display:")
    for col in numerical_cols:
        plot_options[col] = st.sidebar.checkbox(f'Show Distribution of {col}')
    return plot_options


def plot_numerical_distributions(df, numerical_cols, plot_options):
    for col in numerical_cols:
        if plot_options[col]:
            st.subheader(f'Distribution of {col}')

            # Plotting the distribution
            plt.figure(figsize=(10, 6))
            sns.histplot(df[col].dropna(), kde=True)
            plt.title(f'Distribution of {col}')

            # Show the plot using Streamlit
            st.pyplot(plt)

            # Close the plot to avoid overlaps in Streamlit
            plt.clf()


def main(filepath):
    #get the dataset
    df_built, df_land, df = cleaning(filepath)
    # Define the columns to keep for plotting
    columns_to_plot = [
        "Date mutation", "Nature mutation", "Valeur fonciere",
        "Code departement", "Code type local", "Surface reelle bati",
        "Surface terrain", "Nombre pieces principales", "Nature culture"
    ]

    print("getting the df")
    # Prepare the subset of the dataframe
    df_subset = prepare_data_for_plotting(df, columns_to_plot)
    print("succeeded to clean the dataset")

    # Get numerical columns from the subset
    numerical_cols = get_numerical_columns(df_subset)
    print("succeeded to get the numerical columns")

    # Get numerical and categorical columns from the subset
    numerical_cols = df_subset.select_dtypes(include=['float64', 'int64']).columns
    categorical_cols = df_subset.select_dtypes(include=['object']).columns

    print("succeeded to seperate numerical and categorical columns")

    print("starting the plotting")

    # Plot numerical columns using histograms
    for col in numerical_cols:
        print("plotting numerical column: ", col)
        plt.figure(figsize=(10, 6))
        sns.histplot(df_subset[col].dropna(), kde=True)
        plt.title(f'Distribution of {col}')
        plt.show()

    # Plot categorical columns using count plots
    for col in categorical_cols:
        print("plotting categorical column: ", col)
        plt.figure(figsize=(10, 6))
        sns.countplot(y=df_subset[col].dropna(), order=df_subset[col].value_counts().index)
        plt.title(f'Distribution of {col}')
        plt.show()
