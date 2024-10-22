import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tensorflow.python.ops.random_ops import categorical

from dashboard.dataset_cleaning import cleaning
from dashboard.visu_generation import (prepare_data_for_plotting, get_numerical_columns, get_categorical_columns,
                                       plot_categorical_distribution, plot_numerical_distribution,
                                       plot_numerical_vs_valeur_fonciere, plot_categorical_vs_valeur_fonciere,
                                       plot_valeur_fonciere_range)

@st.cache_data
def prepare_data_for_plotting(df, columns_to_plot):
    return df[columns_to_plot]

def create_plot_options(cols):
    """
    Create a dictionary with column names as keys and False as values
    to initialize the plot options for columns.
    """
    return {col: False for col in cols}

def display_cv():
    # Title of the application
    st.markdown("<h1 style='text-align: center;'>Hugo Loreal's Interactive Resume</h1>", unsafe_allow_html=True)

    # Create columns for the personal information section
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### Personal Information")
        st.markdown(
            """
            **Name:** Hugo Loreal  
            **Email:** [hugo.loreal@efrei.net](mailto:hugo.loreal@efrei.net)  
            **Phone:** 06 95 97 42 91  
            **Location:** 136 Boulevard Maxime Gorki, 94800 Villejuif  
            **Looking for Internship:** November 2, 2024 - April 6, 2025  
            """
        )

    with col2:
        st.image("data/IMG_7946.png", caption="Hugo Loreal",
                 width=150)  # Placeholder image for profile picture

    # Use columns to arrange work experience and education side by side
    st.divider()  # Add a divider for better visual separation

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Work Experience & Projects")

        # Work Experiences
        with st.expander("Sales Assistant (Internship) - Darty, Paris"):
            st.write("**Duration:** January 2022 - February 2022")
            st.write("- Addressed customer needs")
            st.write("- Improved teamwork and B2C communication skills")

        with st.expander("Project Manager - SEPEFREI, Villejuif"):
            st.write("**Duration:** November 2021 - July 2022")
            st.write("- Ensured smooth project execution")
            st.write("- Maintained communication with B2B clients")

        # Projects
        with st.expander("Real Estate Value Analysis Project"):
            st.write("- Cleaned and filtered real estate data for exploratory analysis and modeling")
            st.write("- Applied machine learning algorithms like K-Means and linear regression")
            st.write("- Improved proficiency with Python libraries")

    with col2:
        st.markdown("### Education & Semester Abroad")

        # Education
        st.markdown("""
        **EFREI Paris**  
        *Major: Data & AI (2021 - 2026)*  

        **Lycée Descartes**  
        *CPGE MPSI (2020 - 2021)*  

        **Hammond School**  
        *High School (2018 - 2020)*  
        """)

        # Semester Abroad
        st.markdown("""
        **Semester Abroad**  
        *APU (Kuala Lumpur): September - December 2024*  
        """)

    # Skills in two columns
    st.divider()
    st.markdown("### Skills")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Languages")
        st.write("English (Fluent)")
        st.write("French (Mother Tongue)")

    with col2:
        st.markdown("#### Programming Languages")
        st.write("Ocaml, Java, Python (Numpy, Sklearn, Pandas), Javascript, C, C++")

    # Associations
    st.divider()
    st.markdown("### Associations")
    st.write("- Hammond Football Team Receiver, SCISA State Champions (2018 - 2019)")
    st.write("- Volunteer in AFEV, teaching student at Collège Robert Desnos (2021 - 2022)")

    # Download Button at the bottom
    st.write("---")
    st.write("### Download Resume")
    with open("data/CV_Hugo_LOREAL.pdf", "rb") as file:
        btn = st.download_button(
            label="Download Full Resume as PDF",
            data=file,
            file_name="Hugo_Loreal_Resume.pdf",
            mime="application/pdf",
        )


def main(filepath):
    #get the dataset
    df_built, df_land, df = cleaning(filepath)
    # Define the columns to keep for plotting
    columns_list = [
        "Month", "Nature mutation", "Valeur fonciere",
        "Code departement", "Code type local", "Surface reelle bati",
        "Surface terrain", "Nombre pieces principales", "Nature culture"
    ]

    # Prepare the subset of the dataframe
    df_subset = prepare_data_for_plotting(df, columns_list)
    df_built_subset = prepare_data_for_plotting(df_built, columns_list)
    df_land_subset = prepare_data_for_plotting(df_land, columns_list)

    # Sidebar: Section selection
    st.sidebar.title("Navigation")
    section_choice = st.sidebar.radio(
        "Select View",
        options=["See Resume","Data Cleaning Results", "Data Analysis (Plots)", "Valeur Foncière Range Analysis"]
    )
    if section_choice == "See Resume":
        display_cv()
    elif section_choice == "Data Cleaning Results":
        st.header("Data Cleaning Results")

        # Dataset selection
        dataset_choice = st.radio(
            "Choose the dataset to use for plotting",
            options=["All Properties", "Built Properties", "Land Properties"]
        )

        # Assign the selected dataset based on user input
        if dataset_choice == "All Properties":
            selected_df = df_subset
        elif dataset_choice == "Built Properties":
            selected_df = df_built_subset
        elif dataset_choice == "Land Properties":
            selected_df = df_land_subset

        filtered_columns_list=columns_list
        if dataset_choice == "Land Properties":
            filtered_columns_list = [col for col in columns_list if col in[ "Month", "Nature mutation", "Valeur fonciere",
            "Code departement", "Code type local", "Surface terrain", "Nature culture"]]

        # Get numerical and categorical columns for the selected dataset
        numerical_cols = get_numerical_columns(selected_df)
        categorical_cols = get_categorical_columns(selected_df)

        # Select box for both numerical and categorical columns
        selected_col = st.selectbox(
            "Choose a column to plot",
            options=filtered_columns_list,
            help="Choose one column to plot its distribution."
        )

        # Check if the selected column is numerical or categorical and plot
        if selected_col in numerical_cols:
            plot_numerical_distribution(selected_df, selected_col)
        elif selected_col in categorical_cols:
            plot_categorical_distribution(selected_df, selected_col)

    # Section 2: Data Analysis (Plots)
    elif section_choice == "Data Analysis (Plots)":
        st.header("Analysis of Variables Influencing Valeur Foncière")

        # Get numerical and categorical columns for the selected dataset
        numerical_cols = get_numerical_columns(df_built_subset)
        categorical_cols = get_categorical_columns(df_built_subset)

        # Choose a variable to analyze its impact on Valeur Foncière
        st.header("Select a Variable to Analyze Against Valeur Foncière")

        filtered_columns_list = [col for col in columns_list if col != 'Valeur fonciere']

        # Allow the user to select a variable
        selected_var = st.selectbox(
            "Choose a variable",
            options=filtered_columns_list,
            help="Choose one variable to visualize its relationship with Valeur Foncière."
        )

        # Plot based on the type of the selected variable (numerical or categorical)
        if selected_var in numerical_cols:
            plot_numerical_vs_valeur_fonciere(df_built_subset, selected_var)
        elif selected_var in categorical_cols:
            plot_categorical_vs_valeur_fonciere(df_built_subset, selected_var)


    elif section_choice == "Valeur Foncière Range Analysis":
        st.header("Valeur Foncière Range and Surface Reelle Bati Analysis")

        # Convert "Code departement" to string for consistency
        df_built_subset['Code departement'] = df_built_subset['Code departement'].astype(str)
        df_built_subset=df_built_subset[df_built_subset['Nature mutation']=='Vente']

        # Step 1: User selects the department
        department_list = df_built_subset['Code departement'].unique()
        selected_department = st.selectbox('Select Code Departement', sorted(department_list))

        # Step 2: User selects a range of 'Valeur fonciere'
        min_valeur = df_built_subset['Valeur fonciere'].min()
        max_valeur = df_built_subset['Valeur fonciere'].max()
        selected_range = st.slider('Select range of Valeur Foncière',
                                   min_valeur, max_valeur, (min_valeur, max_valeur))
        plot_valeur_fonciere_range(df_built_subset, selected_department, selected_range)

    # Button to clear the cache
    if st.sidebar.button("Clear Cache"):
        st.cache_data.clear()
        st.success("Cache cleared successfully!")
if __name__ == "__main__":
    main()
