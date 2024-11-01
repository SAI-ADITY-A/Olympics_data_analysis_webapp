import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

import preprocessor, helper


# Preprocessing the df's
df = pd.read_csv('athlete_events.csv')
region_df = pd.read_csv('noc_regions.csv')

df = preprocessor.preprocess(df,region_df)


st.sidebar.title("Olympics Analysis")
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Olympic_rings_without_rims.svg/640px-Olympic_rings_without_rims.svg.png")


user_menu = st.sidebar.radio(
    'Select from below',
    ('Medal Tally', 'Overall view', 'Country-wise Analysis', 'Athelete-wise analysis')
)

# st.dataframe(df)

if user_menu == 'Medal Tally':
    st.sidebar.header("Medal Tally")
    years, country = helper.country_year_list(df)

    selected_year = st.sidebar.selectbox('Select an year', years)
    selected_country = st.sidebar.selectbox('Select a country', country)

    medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)

    if selected_year == 'Overall' and selected_country == 'Overall':
        st.title("Overall Tally")

    if selected_year != 'Overall' and selected_country == 'Overall':
        st.title("Medal Tally in " + str(selected_year) + " Olympics")

    if selected_year == 'Overall' and selected_country != 'Overall':
        st.title(selected_country + " overall performance")

    if selected_year != 'Overall' and selected_country != 'Overall':
        st.title(selected_country + " performance in " + str(selected_year) + " Olympics")

    st.table(medal_tally)


if user_menu == 'Overall view':
    editions = df['Year'].unique().shape[0] - 1
    cities = df['City'].unique().shape[0]
    Nations = df['region'].unique().shape[0]
    Sports = df['Sport'].unique().shape[0]
    Events = df['Event'].unique().shape[0]
    Athletes = df['Name'].unique().shape[0]

    st.title("Top Statistics")

    col1,col2,col3 = st.columns(3)
    with col1:
        st.header("Editions")
        st.title(editions)
    with col2:
        st.header("Hosts")
        st.title(cities)
    with col3:
        st.header("Sports")
        st.title(Sports)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Events")
        st.title(Events)
    with col2:
        st.header("Nations")
        st.title(Nations)
    with col3:
        st.header("Athletes")
        st.title(Athletes)

    nations_over_time = helper.data_over_time(df, 'region')
    fig = px.line(nations_over_time, x='Edition', y='region')
    st.title("Participating Nations over the years")
    st.plotly_chart(fig)

    Events_over_time = helper.data_over_time(df, 'Event')
    fig = px.line(Events_over_time, x='Edition', y='Event')
    fig.update_traces(line_color = 'green')
    st.title("Events over the years")
    st.plotly_chart(fig)

    athletes_over_time = helper.data_over_time(df, 'Name')
    fig = px.line(athletes_over_time, x='Edition', y='Name')
    fig.update_traces(line_color = 'orange')
    st.title("Athletes over the years")
    st.plotly_chart(fig)

    st.title("No. of Events over time (every sport)")
    fig, ax = plt.subplots(figsize = (20, 20))
    fig,ax = plt.subplots(figsize=(20,20))
    x = df.drop_duplicates(['Year', 'Sport', 'Event'])
    ax = sns.heatmap(x.pivot_table(index='Sport', columns='Year', values='Event', aggfunc='count').fillna(0).astype('int'), annot=True)
    st.pyplot(fig)

    st.title("Most Successful Athletes")
    sports_list = df['Sport'].unique().tolist()

    sports_list.sort()
    sports_list.insert(0, 'Overall')

    selected_sport = st.selectbox('Select a sport',sports_list )

    fig = helper.most_successful_athlete(df, selected_sport)
    st.table(fig)


if user_menu == 'Country-wise Analysis':

    st.sidebar.title('Country-wise Analysis')

    country_list = df['region'].dropna().unique().tolist()
    country_list.sort()

    country_selected = st.sidebar.selectbox('Select a Country',country_list)

    country_df = helper.yearwise_medal_tally(df,country_selected)
    fig = px.line(country_df, x="Year", y="Medal")
    st.title(country_selected + " Medal Tally over the years")
    fig.update_traces(line_color = 'salmon')
    st.plotly_chart(fig)

    st.title(country_selected + " excels in the following sports")
    pt = helper.country_event_heatmap(df,country_selected)
    fig, ax = plt.subplots(figsize=(20, 20))
    ax = sns.heatmap(pt,annot=True)
    st.pyplot(fig)

    st.title("Top 10 Athletes of " + country_selected)
    top10_df = helper.most_successful_athlete_countrywise(df, country_selected)
    st.table(top10_df)


if user_menu == 'Athelete-wise analysis':

    athlete_df = df.drop_duplicates(subset=['Name', 'region'])

    x1 = athlete_df['Age'].dropna()
    x2 = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna()
    x3 = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna()
    x4 = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()

    plt.figure(figsize=(10, 6))
    sns.kdeplot(x=x1, label='Overall Age', shade=True)
    sns.kdeplot(x=x2, label='Gold Medalist', shade=True)
    sns.kdeplot(x=x3, label='Silver Medalist', shade=True)
    sns.kdeplot(x=x4, label='Bronze Medalist', shade=True)

    # Plot labels
    plt.title("Distribution of Age by Medal Type")
    plt.xlabel("Age")
    plt.ylabel("Density")
    plt.legend()

    # Display in Streamlit
    st.title("Distribution of Age")
    st.pyplot(plt)


    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'Overall')

    st.title('Height Vs Weight')
    selected_sport = st.selectbox('Select a Sport', sport_list)
    temp_df = helper.weight_v_height(df,selected_sport)
    fig,ax = plt.subplots()
    ax = sns.scatterplot(x = temp_df['Weight'], y = temp_df['Height'], hue=temp_df['Medal'], style=temp_df['Sex'], s=10)
    st.pyplot(fig)

    st.title("Men Vs Women Participation Over the Years")
    final = helper.men_vs_women(df)
    fig = px.line(final, x="Year", y=["Male", "Female"])
    fig.update_layout(autosize=False, width=1000, height=600)
    st.plotly_chart(fig)
