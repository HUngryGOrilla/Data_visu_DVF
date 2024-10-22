import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from tensorflow.python.ops.random_ops import categorical
import streamlit as st
import plotly.express as px
import geopandas as gpd
import geoviews as gv
from geoviews import dim
import hvplot.pandas
import pyogrio
import folium
from streamlit_folium import st_folium
import plotly.express as px
import streamlit as st
gv.extension('bokeh')

def prepare_data_for_plotting(df, columns_to_plot):
    """
    Subset the DataFrame and keep only the desired columns for plotting.

    Parameters:
        df (pd.DataFrame): The DataFrame to process.
        columns_to_plot (list): List of columns to retain for plotting.

    Returns:
        pd.DataFrame: Subset of the DataFrame with only the columns to plot.
    """
    return df[columns_to_plot]



def get_numerical_columns(df):
    """
    Get the numerical columns from the DataFrame.

    Parameters:
        df (pd.DataFrame): The DataFrame to check for numerical columns.

    Returns:
        list: List of numerical column names.
    """
    numerical_cols_name = ["Month", "Valeur fonciere", "Surface reelle bati", "Surface terrain",
                           "Nombre pieces principales"]
    #numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns
    numerical_cols = [col for col in numerical_cols_name if col in df.columns]
    return numerical_cols

def get_categorical_columns(df):
    """
    Get the numerical columns from the DataFrame.

    Parameters:
        df (pd.DataFrame): The DataFrame to check for numerical columns.

    Returns:
        list: List of numerical column names.
    """
    categorical_cols_name = ["Nature mutation", "Code departement", "Code type local", "Nature culture"]
    #categorical_cols = df.select_dtypes(include=['object']).columns
    categorical_cols = [col for col in  df.columns if col in categorical_cols_name]
    df[categorical_cols] = df[categorical_cols].apply(
        lambda x: x.astype('category') if pd.api.types.is_numeric_dtype(x) else x)
    return categorical_cols

# Mapping month numbers to month names
month_mapping = {1: 'January', 2: 'February', 3: 'March', 4: 'April',
                 5: 'May', 6: 'June', 7: 'July', 8: 'August',
                 9: 'September', 10: 'October', 11: 'November', 12: 'December'}

type_local_mapping = {
    1: 'Maison',
    2: 'Appartement',
    3: 'Dépendance',
    4: 'Local'
}

def plot_numerical_distribution(df, col):
    """Plot interactive distribution for the selected numerical column."""
    print(f"Interactive numerical Distribution of {col}")

    # Create an interactive histogram using Plotly
    fig = px.histogram(
        df,
        x=col,
        nbins=30,  # You can control the number of bins here
        marginal="box",  # Adds a box plot for additional context
        title=f"Distribution of {col}",
    )

    if col.lower() == 'month':
        fig.update_xaxes(tickvals=list(month_mapping.keys()), ticktext=list(month_mapping.values()))

    # Update layout to customize the look of the plot
    fig.update_layout(
        xaxis_title=col,
        yaxis_title='Frequency',
        bargap=0.1,  # Adjust gap between bars
        hovermode="x unified"  # Make hover info consistent
    )

    # Display the plot using Streamlit
    st.plotly_chart(fig)



def plot_categorical_distribution(df, col):
    """Plot interactive distribution for the selected categorical column."""
    print(f"Interactive categorical Distribution of {col}")

    if col.lower() == 'code type local':
        # Convert 'Code type local' to integer to ensure consistency
        df[col] = df[col].astype(float).astype('Int64')
    # Convert to string to ensure consistent categorical treatment
    df[col] = df[col].astype(str)

    # Use value_counts() to count occurrences and reset the index to turn it into a DataFrame
    count_df = df[col].value_counts().reset_index()
    count_df.columns = [col, 'count']  # Rename the columns for better clarity

    # Sort by count (descending)
    count_df = count_df.sort_values(by='count', ascending=False)

    # Extract the sorted categories (in the order of appearance)
    sorted_categories = count_df[col].tolist()

    # Create an interactive bar chart using Plotly
    fig = px.bar(
        count_df,  # DataFrame with category counts
        x=col,
        y='count',
        title=f"Distribution of {col}",
        labels={col: col, 'count': 'Frequency'},  # Label the axes
    )

    if col.lower() == 'code type local':
        fig.update_xaxes(tickvals=list(type_local_mapping.keys()), ticktext=list(type_local_mapping.values()))

    # Explicitly set the category order based on the sorted data, treat the axis as categorical
    fig.update_xaxes(
        categoryorder='array',  # Use the explicit order defined by sorted_categories
        categoryarray=sorted_categories,  # Sorted categories based on frequency
        type='category'  # Force the axis to be treated as categorical
    )

    # Update layout to customize the look of the plot
    fig.update_layout(
        xaxis_title=col,
        yaxis_title='Frequency',
        hovermode="x unified",  # Make hover info consistent
        bargap=0.1  # Adjust the gap between bars
    )

    # Display the plot using Streamlit
    st.plotly_chart(fig)


def plot_numerical_vs_valeur_fonciere(df, col):
    """Plot interactive line plot for mean Valeur Foncière for values of a numerical variable."""
    st.write(f"Mean Valeur Foncière across {col}")

    # Calculate mean Valeur Foncière for each unique value in the numerical variable
    mean_valeur_fonciere = df.groupby(col)['Valeur fonciere'].mean().reset_index()

    # Create an interactive line plot using Plotly
    fig = px.line(
        mean_valeur_fonciere,
        x=col,
        y='Valeur fonciere',
        title=f'Mean Valeur Foncière for {col}',
        labels={col: col, 'Valeur fonciere': 'Mean Valeur Foncière'},
        markers=True  # Add markers to each data point
    )

    if col.lower() == 'month':
        fig.update_xaxes(tickvals=list(month_mapping.keys()), ticktext=list(month_mapping.values()))

    # Customize layout
    fig.update_layout(
        xaxis_title=col,
        yaxis_title='Mean Valeur Foncière',
        hovermode='x unified'  # Show hover info for all data points along the x-axis
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig)

def plot_categorical_vs_valeur_fonciere(df, col):
    """Plot interactive map for 'Code departement' or a bar plot for other categorical variables."""
    st.write(f"Mean Valeur Foncière across categories of {col}")
    df[col] = df[col].astype(str)

    # Special case for "Code departement" to display the map
    if col == 'Code departement':
        # Calculate mean price per square meter for each department
        df['Prix_m2'] = df['Valeur fonciere'] / df['Surface reelle bati']
        avg_price_per_department = df.groupby('Code departement')['Prix_m2'].median().reset_index()

        # Use pyogrio to load the GeoJSON data
        sf = gpd.GeoDataFrame.from_features(pyogrio.read_dataframe('data/france-geojson/departements-version-simplifiee.geojson'))

        # Ensure proper formatting of department codes (e.g., padding with zeros if necessary)
        sf['code'] = sf['code'].astype(str).apply(lambda x: x.zfill(2) if x.isdigit() else x)
        avg_price_per_department['Code departement'] = avg_price_per_department['Code departement'].astype(str).apply(lambda x: x.zfill(2) if x.isdigit() else x)

        # Merge the GeoDataFrame with the price data
        df_merged = pd.merge(sf, avg_price_per_department[['Code departement', 'Prix_m2']], left_on='code', right_on='Code departement', how='left')

        # Check if the CRS is set; if not, set it to a default CRS (for example, 'EPSG:4326')
        if df_merged.crs is None:
            df_merged.set_crs(epsg=4326, inplace=True)  # Assuming the original data is in WGS84 (EPSG:4326)

        # Ensure the GeoDataFrame is in the WGS84 projection (EPSG:4326) for folium compatibility
        df_merged = df_merged.to_crs(epsg=4326)

        # Initialize a folium map centered on France
        m = folium.Map(location=[46.603354, 1.888334], zoom_start=6)

        # Add the GeoJSON layer to the folium map
        folium.Choropleth(
            geo_data=df_merged,
            name='choropleth',
            data=df_merged,
            columns=['code', 'Prix_m2'],
            key_on='feature.properties.code',  # Match with 'code' field in GeoJSON
            fill_color='YlGnBu',
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name='Prix moyen par mètre carré',
        ).add_to(m)

        # Display the map in Streamlit
        st.write("Interactive map showing average price per square meter by department:")
        st_folium(m, width=700, height=500)

    else:
        # For other categorical variables, create a bar plot
        mean_valeur_fonciere = df.groupby(col)['Valeur fonciere'].mean().reset_index()

        # Create an interactive bar plot using Plotly
        fig = px.bar(
            mean_valeur_fonciere,
            x=col,
            y='Valeur fonciere',
            title=f"Mean Valeur Foncière for {col}",
            labels={col: col, 'Valeur fonciere': 'Mean Valeur Foncière'}
        )
        if col.lower() == 'code type local':
            fig.update_xaxes(tickvals=list(type_local_mapping.keys()), ticktext=list(type_local_mapping.values()))
        # Customize layout
        fig.update_layout(
            xaxis_title=col,
            yaxis_title='Mean Valeur Foncière',
            hovermode='x unified',  # Show hover info for all data points along the x-axis
            xaxis={'categoryorder': 'total descending'}  # Order bars by descending frequency
        )

        # Display the plot in Streamlit
        st.plotly_chart(fig)
def plot_valeur_fonciere_range(df, selected_department, selected_range):
    """Plot number of properties for each value of 'Surface reelle bati' and 'Code type local' in a selected range of Valeur Foncière."""

    # Filter the data based on selected department and valeur foncière range
    filtered_df = df[
        (df['Code departement'] == selected_department) &
        (df['Valeur fonciere'] >= selected_range[0]) &
        (df['Valeur fonciere'] <= selected_range[1])
    ]

    filtered_df['Code type local'] = filtered_df['Code type local'].map(type_local_mapping)

    # Count the number of properties for each value of 'Surface reelle bati' and 'Code type local'
    if not filtered_df.empty:
        # Group by both 'Surface reelle bati' and 'Code type local'
        surface_bati_distribution = filtered_df.groupby(['Surface reelle bati', 'Code type local']).size().reset_index(name='Count')
        color_sequence = ['#ff0000', '#0000ff', '#00ff00', '#800080']
        # Create a bar plot using Plotly, color-coded by 'Code type local'
        fig = px.bar(
            surface_bati_distribution,
            x='Surface reelle bati',
            y='Count',
            color='Code type local',  # This ensures that each 'Code type local' gets a separate color
            title=f"Distribution of Surface Reelle Bati by Code Type Local in {selected_department} for Valeur Foncière Range {selected_range}",
            labels={'Surface reelle bati': 'Surface Reelle Bati (m²)', 'Count': 'Number of Properties', 'Code type local': 'Type'},
            text='Count',
            color_discrete_sequence = color_sequence
        )

        # Display the bar plot in Streamlit
        st.plotly_chart(fig)

    else:
        st.write(f"No data available for Code Departement {selected_department} in the selected range.")