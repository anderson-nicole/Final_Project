import pandas as pd
import streamlit as st
import altair as alt
from vega_datasets import data

@st.cache_data
def load_data(url):
        df = pd.read_csv(url)
        return df

df = load_data("https://raw.githubusercontent.com/anderson-nicole/Final_Project/refs/heads/main/data/hospital_reviews_cleaned.csv")

st.title("2024 Patient Survey Results for US Hospitals")

st.markdown("Hospital Consumer Assessment of Healthcare Providers and Systems (HCAHPS) is a national survey taken by those who had a stay at an in-patient hospital to assess quality of care recieved. This project aims to provide an easier way to review the information on the hospitals from a national to a facility level. The data original comes from CMS and can be found [here](https://data.cms.gov/provider-data/dataset/dgck-syfz#data-table)")

star_df = df[df["HCAHPS Measure ID"].str.contains("H_STAR_RATING")]
avg_star_rating_by_state = star_df.groupby('State')["Patient Survey Star Rating"].mean().reset_index()

states = alt.topo_feature(data.us_10m.url, 'states')
# states = load_data("https://raw.githubusercontent.com/vega/vega/refs/heads/main/docs/data/us-10m.json") <-- Too slow to load on startup 

state_codes = load_data("https://raw.githubusercontent.com/kjhealy/fips-codes/refs/heads/master/state_fips_master.csv")
state_codes = state_codes[["fips","state_abbr","state_name"]]

avg_star_rating_by_state = avg_star_rating_by_state.merge(state_codes, left_on='State', right_on='state_abbr', how='left')

choropleth = alt.Chart(states).mark_geoshape().encode(
    color=alt.Color('Patient Survey Star Rating:Q', scale=alt.Scale(scheme='blues'), title='Average Star Rating'),
    tooltip= [alt.Tooltip("state_name:N", title="State: "),
              alt.Tooltip("Patient Survey Star Rating:Q", title="Average Rating:  ",format=".2f")]
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(avg_star_rating_by_state, 'fips', ['Patient Survey Star Rating',"state_name"])
).properties(
    width=800,
    height=400,
    title='Average Hospital 5-Star Rating by State'
).project(
    type='albersUsa'
)

st.altair_chart(choropleth)

avg_star_rating_by_state = star_df.groupby('State')["Patient Survey Star Rating"].mean().reset_index()
