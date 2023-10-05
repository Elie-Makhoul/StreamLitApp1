import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_dynamic_filters import DynamicFilters
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

# Load the data


df = pd.read_csv("csv/project_Data_modified.csv")

# Set page configuration
st.set_page_config(page_title="Project's Dashboard",
                   page_icon=":bar_chart:", layout="wide")


# Read the CSS file
with open("css/styles.css") as f:
    css = f.read()

# Apply the CSS using st.markdown
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# ---- SIDEBAR ----

# renaming columns

df["project Name"] = df["projectName"]
df["sprint Name"] = df["sprintName"]
df["story Type"] = df["storyType"]

dynamic_filters = DynamicFilters(
    df, filters=['project Name', 'sprint Name', 'story Type'], )


with st.sidebar:
    st.sidebar.header("Please Filter Here:")
    dynamic_filters.display_filters()


filtered_df = dynamic_filters.filter_except()


# Calculate the distinct count of 'sprintId'
sprints_distinct_count = filtered_df['sprintId'].nunique()

# Calculate the count of the stories
story_count = filtered_df['storyKey'].count()


# Rename the "storystatus(list)" column
filtered_df = filtered_df.rename(columns={'storystatus(list)': 'story status'})


# Calculate the story counts per project and story status
project_story_count = filtered_df.groupby(['projectName', 'story status'])[
    'storyKey'].count().reset_index()
project_story_count.columns = ['projectName',
                               'story status',  'storyKey_count']

sprint_df = filtered_df[['projectName', 'sprintName']]

merged_df = pd.merge(project_story_count, sprint_df,
                     on='projectName', how='left')


# Create the column chart using Plotly Express

color_map = {'done': 'green', 'not done': 'red'}

fig1 = px.bar(
    project_story_count,
    x='projectName',
    y='storyKey_count',
    color='story status',
    barmode='group',
    title='Stories by Project',
    labels={'projectName': 'Project', 'storyKey_count': 'Story'},
    color_discrete_map=color_map,


)
# Update hover data to show the count of each story status
fig1.update_traces(texttemplate='%{y}', textposition='outside')
fig1.update_layout(legend_title_text='Story Status')

fig1.update_layout(
    font=dict(
        family='Arial, sans-serif',
        size=11,
        color='black',
    ),


    legend=dict(
        orientation='h',  # Set the orientation to horizontal
        x=0,  # Move the legend to the left
        y=1.1  # Adjust the position if needed
    ),

    height=600,

)


# Calculate story counts by story type
storytype_story_count = filtered_df.groupby(
    'storyType').size().reset_index(name='story_count')

# If there's only one story type, add a default row with count 1
if len(storytype_story_count) == 1:
    default_row = pd.DataFrame(
        {'storyType': ['Default'], 'story_count': [0]}, )
    storytype_story_count = pd.concat(
        [storytype_story_count, default_row], ignore_index=True)


# Create a treemap using Plotly Express
fig2 = px.treemap(
    storytype_story_count,
    path=['storyType'],
    values='story_count',
    title='Story Counts by Story Type',
    custom_data=['story_count']
)

fig2.update_layout(
    font=dict(
        family='Arial, sans-serif',
        size=16,
        color='black'
    ),
    height=600
)

fig2.update_traces(

    texttemplate='%{label}: %{customdata}</span>'

)


# Display the treemap
# st.plotly_chart(fig2)


# Calculate the count of each story status
status_counts = filtered_df['story status'].value_counts()


# Create a pie chart
fig3 = px.pie(status_counts, values=status_counts,
              names=status_counts.index, title='Story Status Distribution', color_discrete_sequence=['green', 'red'])

# Display the pie chart
# st.plotly_chart(fig3)


# Rename the "parentId(List)" column
filtered_df = filtered_df.rename(columns={'parentId(List)': 'parent Id'})


# Count stories for each parent ID
parent_id_counts = filtered_df['parent Id'].value_counts()


# Create another pie chart
fig4 = px.pie(
    parent_id_counts,
    values=parent_id_counts,
    names=parent_id_counts.index,
    hole=0.3,
    title='Story by Parent ID',
)


with st.container():
    # Display KPIs in a row
    # Adjust the width ratios as needed
    col1, col2,  = st.columns([1, 1],  gap="medium")
    with col1:
        st.markdown(
            f'<div class="card">'
            f'<h3>Number of Sprints</h3>'
            f'<h1>{sprints_distinct_count}</h1>'
            f'</div>',
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f'<div class="card">'
            f'<h3>Number of Stories</h3>'
            f'<h1>{story_count}</h1>'
            f'</div>',
            unsafe_allow_html=True
        )

    # Display Graphs in a row
    # Adjust the width ratios as needed
    col3, col4 = st.columns([1, 1], gap="medium")
    with col3:
        st.plotly_chart(fig1, use_container_width=True)
    with col4:
        st.plotly_chart(fig2, use_container_width=True)

    col5, col6 = st.columns([1, 1], gap="medium")

    with col5:
        st.plotly_chart(fig3, use_container_width=True)

    with col6:
        st.plotly_chart(fig4, use_container_width=True)
