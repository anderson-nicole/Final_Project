import pandas as pd
import streamlit as st
import altair as alt
import numpy as np

st.set_page_config(layout="wide")

@st.cache_data
def load_data(url):
        df = pd.read_csv(url)
        return df

if "selected_state" not in st.session_state:
    st.session_state.selected_state = None
if "selected_city" not in st.session_state:
    st.session_state.selected_city = None
if "selected_hospital" not in st.session_state:
    st.session_state.selected_hospital = None

df = load_data("https://raw.githubusercontent.com/anderson-nicole/Final_Project/refs/heads/main/data/hospital_reviews_cleaned.csv)

st.title("2024 Hospital Overview")
st.subheader("Select a hospital you would like to view")
with st.container():
    col1, col2, col3 = st.columns(3)

    states = list(df["State"].unique())
    states.sort()

    with col1:
        states_full = ["Select a State"] + states
        selected_state = st.selectbox("Select a State", states_full,
                                      index = states_full.index(st.session_state.selected_state) if st.session_state.selected_state else 0)
        
        if selected_state != st.session_state.selected_state:
            st.session_state.selected_city = None
            st.session_state.selected_hospital = None
        
        st.session_state.selected_state = selected_state

    with col2:
        if selected_state != "Select a State":
            cities = df[df["State"] == selected_state]["County/Parish"].unique()
            cities.sort()
            cities_full = ["Select a City/County"] + list(cities)
            selected_city = st.selectbox("Select a City/County", cities_full,
                                         index = cities_full.index(st.session_state.selected_city) if st.session_state.selected_city else 0)
        else:
            selected_city = st.selectbox("Select a City/County", ["Select a City/County"], disabled=True)

        if selected_city != st.session_state.selected_city:
            st.session_state.selected_hospital = None
        st.session_state.selected_city = selected_city

    with col3:
        if selected_city != "Select a City/County" and selected_city != "":
            hospitals = df[(df["State"] == selected_state) & (df["County/Parish"] == selected_city)]["Facility Name"].unique()
            hospitals.sort()
            hospitals_full = ["Select a Hospital"] + list(hospitals)
            selected_hospital = st.selectbox("Select a Hospital", hospitals_full,
                                              index = hospitals_full.index(st.session_state.selected_hospital) if st.session_state.selected_hospital else 0)
        else:
            selected_hospital = st.selectbox("Select a Hospital", ["Select a Hospital"], disabled=True)
        st.session_state.selected_hospital = selected_hospital


if selected_hospital != "Select a Hospital":
    hospital_data = df[(df["State"] == selected_state) & 
                       (df["County/Parish"] == selected_city) & 
                       (df["Facility Name"] == selected_hospital)]

    if hospital_data["Missing Flag"].any() == 1:
        st.markdown("#### No data for this location")
    else: 
        
        star_rating = hospital_data.loc[hospital_data["HCAHPS Measure ID"] == "H_STAR_RATING", "Patient Survey Star Rating"]
        if star_rating.isnull().any():
            st.markdown(f"#### Overall Rating: Not Available") 
        else:
            stars = int(star_rating.iloc[0]) * "⭐"    
            st.markdown(f"#### Overall Rating: {stars}") 

        hospital_data['HCAHPS Answer Percent'] = pd.to_numeric(hospital_data['HCAHPS Answer Percent'], errors='coerce')
        comp1 = hospital_data[hospital_data["HCAHPS Measure ID"].str.contains("H_COMP_1")]
        comp2 = hospital_data[hospital_data["HCAHPS Measure ID"].str.contains("H_COMP_2")]
        comp3 = hospital_data[hospital_data["HCAHPS Measure ID"].str.contains("H_COMP_3")]
        comp5 = hospital_data[hospital_data["HCAHPS Measure ID"].str.contains("H_COMP_5")]
        comp6 = hospital_data[hospital_data["HCAHPS Measure ID"].str.contains("H_COMP_6")]
        comp7 = hospital_data[hospital_data["HCAHPS Measure ID"].str.contains("H_COMP_7")]

        suffixes_1 = {
            "A_P": "Always",
            "SN_P": "Sometimes or Never",
            "U_P": "Usually"
        }

        suffixes_2 = {
            "N_P": "No",
            "Y_P": "Yes"
        }

        suffixes_3 = {
            "7_A": "Agree",
            "D_SD": "Disagree or Strongly Disagree",
            "7_SA": "Strongly Agree"
        }

        comp1["Suffix"] = comp1["HCAHPS Measure ID"].str.split("_").str[-2] + "_" + comp1["HCAHPS Measure ID"].str.split("_").str[-1]
        comp1 = comp1[comp1["Suffix"].str.contains("A_P|SN_P|U_P")]
        comp1["Suffix"] = comp1["Suffix"].map(suffixes_1)
        
        comp1_chart = (
            alt.Chart(comp1)
            .mark_bar()
            .transform_calculate(
                percentage = 'datum["HCAHPS Answer Percent"] / 100'
            )
            .encode(
                x=alt.X("Suffix:N", title="Response", sort=["Always","Usually","Sometimes or Never"],
                        axis=alt.Axis(labelAngle=0)),
                y=alt.Y("HCAHPS Answer Percent:Q", title="Percentage"),
                color=alt.Color("Suffix:N", title="Response Type",legend=None),
                tooltip= alt.Tooltip("percentage:Q", title="Answer Percent", format=".0%")
            )
            .properties(
                title="How Often Nurses Communicated Well",
                width=600,
                height=400
            )
        )

    
        comp2["Suffix"] = comp2["HCAHPS Measure ID"].str.split("_").str[-2] + "_" + comp2["HCAHPS Measure ID"].str.split("_").str[-1]
        comp2 = comp2[comp2["Suffix"].str.contains("A_P|SN_P|U_P")]
        comp2["Suffix"] = comp2["Suffix"].map(suffixes_1)
        

        # Create a bar chart
        comp2_chart = (
            alt.Chart(comp2)
            .mark_bar()
            .transform_calculate(
                percentage = 'datum["HCAHPS Answer Percent"] / 100'
            )
            .encode(
                x=alt.X("Suffix:N", title="Response", sort=["Always","Usually","Sometimes or Never"],
                        axis=alt.Axis(labelAngle=0)),
                y=alt.Y("HCAHPS Answer Percent:Q", title="Percentage"),
                color=alt.Color("Suffix:N", title="Response Type",legend=None),
                tooltip= alt.Tooltip("percentage:Q", title="Answer Percent", format=".0%")
            )
            .properties(
                title="How Often Doctors Communicated Well",
                width=600,
                height=400
            )
        )

        comp3["Suffix"] = comp3["HCAHPS Measure ID"].str.split("_").str[-2] + "_" + comp3["HCAHPS Measure ID"].str.split("_").str[-1]
        comp3 = comp3[comp3["Suffix"].str.contains("A_P|SN_P|U_P")]
        comp3["Suffix"] = comp3["Suffix"].map(suffixes_1)

        comp3_chart = (
            alt.Chart(comp3)
            .mark_bar()
            .transform_calculate(
                percentage = 'datum["HCAHPS Answer Percent"] / 100'
            )
            .encode(
                x=alt.X("Suffix:N", title="Response", sort=["Always","Usually","Sometimes or Never"],
                        axis=alt.Axis(labelAngle=0)),
                y=alt.Y("HCAHPS Answer Percent:Q", title="Percentage"),
                color=alt.Color("Suffix:N", title="Response Type",legend=None),
                tooltip= alt.Tooltip("percentage:Q", title="Answer Percent", format=".0%")
            )
            .properties(
                title="How Often Patient Recieved Help As Soon As They Wanted",
                width=600,
                height=400
            )
        )

        comp5["Suffix"] = comp5["HCAHPS Measure ID"].str.split("_").str[-2] + "_" + comp5["HCAHPS Measure ID"].str.split("_").str[-1]
        comp5 = comp5[comp5["Suffix"].str.contains("A_P|SN_P|U_P")]
        comp5["Suffix"] = comp5["Suffix"].map(suffixes_1)

        comp5_chart = (
            alt.Chart(comp5)
            .mark_bar()
            .transform_calculate(
                percentage = 'datum["HCAHPS Answer Percent"] / 100'
            )
            .encode(
                x=alt.X("Suffix:N", title="Response", sort=["Always","Usually","Sometimes or Never"],
                        axis=alt.Axis(labelAngle=0)),
                y=alt.Y("HCAHPS Answer Percent:Q", title="Percentage"),
                color=alt.Color("Suffix:N", title="Response Type",legend=None),
                tooltip= alt.Tooltip("percentage:Q", title="Answer Percent", format=".0%")
            )
            .properties(
                title="How Often Staff Explained Medications Before Giving Them",
                width=600,
                height=400
            )
        )

        comp6["Suffix"] = comp6["HCAHPS Measure ID"].str.split("_").str[-2] + "_" + comp6["HCAHPS Measure ID"].str.split("_").str[-1]
        comp6 = comp6[comp6["Suffix"].str.contains("N_P|Y_P")]
        comp6["Suffix"] = comp6["Suffix"].map(suffixes_2)

        comp6_chart = (
            alt.Chart(comp6)
            .mark_bar()
            .transform_calculate(
                percentage = 'datum["HCAHPS Answer Percent"] / 100'
            )
            .encode(
                x=alt.X("Suffix:N", title="Response", sort=["Yes","No"],
                        axis=alt.Axis(labelAngle=0)),
                y=alt.Y("HCAHPS Answer Percent:Q", title="Percentage"),
                color=alt.Color("Suffix:N", title="Response Type",legend=None),
                tooltip= alt.Tooltip("percentage:Q", title="Answer Percent", format=".0%")
            )
            .properties(
                title="Were Given Information On What To Do When Discharged",
                width=600,
                height=400
            )
        )

        comp7["Suffix"] = comp7["HCAHPS Measure ID"].str.split("_").str[-2] + "_" + comp7["HCAHPS Measure ID"].str.split("_").str[-1]
        comp7 = comp7[comp7["Suffix"].str.contains("_A|D_SD|_SA")]
        comp7["Suffix"] = comp7["Suffix"].map(suffixes_3)

        comp7_chart = (
            alt.Chart(comp7)
            .mark_bar()
            .transform_calculate(
                percentage = 'datum["HCAHPS Answer Percent"] / 100'
            )
            .encode(
                x=alt.X("Suffix:N", title="Response", sort=["Strongly Agree","Agree","Disagree or Strongly Disagree"],
                        axis=alt.Axis(labelAngle=0)),
                y=alt.Y("HCAHPS Answer Percent:Q", title="Percentage"),
                color=alt.Color("Suffix:N", title="Response Type",legend=None),
                tooltip= alt.Tooltip("percentage:Q", title="Answer Percent", format=".0%")
            )
            .properties(
                title="Patient Understood Their Care When They Left The Hospital",
                width=600,
                height=400
            )
        )

       
        with st.container():
            col1,col2 = st.columns(2)

            with col1 :
                st.altair_chart(comp1_chart)
                st.altair_chart(comp3_chart)
                st.altair_chart(comp6_chart)
                

            with col2:
                st.altair_chart(comp2_chart)
                st.altair_chart(comp5_chart)
                st.altair_chart(comp7_chart)          
                
        st.dataframe(hospital_data)
