import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static
from pathlib import Path

# Load the data
directory = Path(__file__).parent
nocs = pd.read_csv(f"{directory}/clean-data/noc_regions.csv")
nocs = nocs.sort_values('region', ascending=True)
region_to_noc = dict(zip(nocs['NOC'], nocs['region']))

# Sidebar for input
st.sidebar.title("Filters")
country = st.sidebar.selectbox("Select a country", list(region_to_noc.keys()), format_func=lambda x: region_to_noc[x], index=list(region_to_noc.keys()).index('FRA'))
include_winter = st.sidebar.checkbox("Include winter games?", True)
only_medalists = st.sidebar.checkbox("Only include medalists?", False)

@st.cache
def load_bios_df():
    bios = pd.read_csv(f'{directory}/clean-data/bios_locs.csv')
    country_df = bios[(bios['born_country'] == country) & (bios['lat'].notna()) & (bios['long'].notna())]
    return country_df

@st.cache
def load_results_df():
    df = pd.read_csv(f'{directory}/clean-data/results.csv')
    df = df[df['noc'] == country]
    if not include_winter:
        df = df[df['type'] == 'Summer']
    if only_medalists:
        df = df[df['medal'].notna()]
    return df

@st.cache
def get_medals():
    results = load_results_df()
    medals = results[(results['medal'].notna()) & (~results['event'].str.endswith('(YOG)'))]
    medals_filtered = medals.drop_duplicates(['year', 'type', 'discipline', 'noc', 'event', 'medal'])
    medals_by_year = medals_filtered.groupby(['noc', 'year'])['medal'].count().loc[country]
    return medals_by_year.reset_index()

# Display medals by year
st.title("Medals by Year")
medals_df = get_medals()
fig, ax = plt.subplots()
ax.plot(medals_df['year'], medals_df['medal'])
ax.set_xlabel('Year')
ax.set_ylabel('Medal Count')
ax.set_title('Medals by Year')
st.pyplot(fig)

# Display heatmap of athletes
st.title("Heatmap of Athletes")
bios_df = load_bios_df()
m = folium.Map(location=[bios_df['lat'].mean(), bios_df['long'].mean()], zoom_start=2)
heat_data = [[row['lat'], row['long']] for index, row in bios_df.iterrows()]
HeatMap(heat_data).add_to(m)
folium_static(m)

# Display results dataframe
st.title("Results")
results_df = load_results_df()
st.dataframe(results_df.head(100))