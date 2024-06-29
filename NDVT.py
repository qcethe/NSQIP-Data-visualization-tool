import os
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import streamlit as st
import base64

st.set_page_config(
    page_title="NSQIP Dashboard",
    page_icon=":books:",
    layout="wide",
    initial_sidebar_state='expanded'
)

# Sidebar
st.sidebar.header("Filter Here:")

# Create file uploader widget
uploaded_files = st.sidebar.file_uploader(
    label="Select Files",
    accept_multiple_files=True,
    type=["xlsx", "csv", "txt"]
)

# Combine uploaded files into a single dataframe
if uploaded_files:
    file_list = []
    for file in uploaded_files:
        filename = file.name
        ext = os.path.splitext(filename)[1]
        if ext == ".xlsx":
            chunks = pd.read_excel(
                io=file,
                engine='openpyxl',
                usecols='A:JP',
                dtype=str,  # read CPT as string data type
                chunksize=10000,  # read 10,000 rows at a time
            )
        elif ext == ".csv":
            chunks = pd.read_csv(file, chunksize=10000)
        else:
            chunks = pd.read_csv(file, delimiter="\t", encoding="ISO-8859-1", chunksize=10000)

        for chunk in chunks:
            file_list.append(chunk)

    df = pd.concat(file_list, axis=0, ignore_index=True)

SurgSpeciality = st.sidebar.multiselect(
    "Select the Surgical Speciality:",
    options=df["SURGSPEC"].unique(),
)

df_selection = df.query("SURGSPEC == @SurgSpeciality")

CPTCode = st.sidebar.multiselect(
    "Select the CPT Codes:",
    options=df_selection["CPT"].unique(),
#    default=df["CPT"].unique()
)

if st.sidebar.button('Download CPTCode Data'):
    # Filter dataframe based on selected CPTCodes
    df_cpt = df_selection.query("CPT in @CPTCode")

    # Create a button to download the CPT data
    csv = df_cpt.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    filename = "_".join(map(str, CPTCode)) + "_NSQIP_Filtered_CPT_Codes.csv"
    file_download_path = st.text_input("Enter path or select download button:")
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Click here to download CPT Data</a>'
    st.markdown(href, unsafe_allow_html=True)

    # Save file to user specified path
    if file_download_path:
        with open(os.path.join(file_download_path, filename), "w") as f:
            f.write(csv)
        st.success(f"{filename} saved to {file_download_path}.")


df_selection = df_selection.query("CPT == @CPTCode")

# Allow user to select X and Y columns for histograms and heatmap
piefig_col = st.sidebar.selectbox(
    "Select a column for the Pie Chart:",
    df_selection.columns.tolist()
)
x_hist_col = st.sidebar.selectbox(
    "Select a column for the X-axis of Histogram:",
    df_selection.columns.tolist()
)

y_hist_col = st.sidebar.selectbox(
    "Select a column for the Y-axis of Histogram:",
    df_selection.columns.tolist()
)

x_heatmap_col = st.sidebar.selectbox(
    "Select a column for the X-axis of Heatmap:",
    df_selection.columns.tolist()
)

y_heatmap_col = st.sidebar.selectbox(
    "Select a column for the Y-axis of Heatmap:",
    df_selection.columns.tolist()
)

# Main page
st.title(":bar_chart: Data Summary")
st.markdown("##")

# Summary of Filtered Stats
counts = df_selection['SEX'].value_counts().to_dict()

# Create two rows of three columns each
top_left, top_middle, top_right = st.columns(3)
middle_left, middle_middle, middle_right = st.columns(3)
bottom_left, bottom_middle, bottom_right = st.columns(3)

# Top row
with top_left:
    fig_heatmap = px.density_heatmap(df_selection, x=x_heatmap_col, y=y_heatmap_col, nbinsx=20, nbinsy=20, color_continuous_scale='Viridis')
    fig_heatmap.update_layout(
        title_text=f"Figure 1: {y_heatmap_col} vs {x_heatmap_col}",
        title_x=0.5,  # center the title
        margin=dict(t=50)  # add some space at the top
    )
    st.plotly_chart(fig_heatmap)
        # Add download button for exporting raw data from the heatmap
    heatmap_data = df_selection[[x_heatmap_col, y_heatmap_col]]
    csv = heatmap_data.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="Figure_1_{x_heatmap_col}_{y_heatmap_col}.csv">Download Raw Figure 1 Data</a>'
    st.sidebar.write(href, unsafe_allow_html=True)

with top_middle:
    selected_col = piefig_col
    counts = df_selection[selected_col].value_counts()
    n_counts = "n=" + str(len(df_selection[selected_col]))
    fig_pie = px.pie(values=counts.tolist(), names=counts.index.tolist())
    fig_pie.update_traces(textinfo='value+text', text=[f'{p:.1%}' for c, p in zip(counts.tolist(), counts.tolist()/counts.sum())])
    fig_pie.update_layout(
        title_text=f"Figure 2: Procedure Counts by {selected_col}, {n_counts}",
        title_x=0.5,  # center the title
        margin=dict(t=50)  # add some space at the top
    )
    st.plotly_chart(fig_pie)
    # Add download button for exporting the pie chart data
    pie_data = pd.DataFrame({'Labels': counts.index.tolist(), 'Counts': counts.tolist()})
    csv = pie_data.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="Figure_2_procedure_counts_by_{selected_col}.csv">Download Raw Figure 2 Data</a>'
    st.sidebar.write(href, unsafe_allow_html=True)



# Bottom row
with middle_left:
    fig_hist_y = px.histogram(df_selection, y=y_hist_col, nbins=20, color_discrete_sequence=['grey', 'green'])
    fig_hist_y.update_layout(
        title_text=f"Figure 3: Histogram of {y_hist_col}",
        title_x=0.5,  # center the title
        margin=dict(t=50)  # add some space at the top
    )
    st.plotly_chart(fig_hist_y)
    # Add download button for exporting the histogram data
    hist_data = df_selection[[y_hist_col]]
    csv = hist_data.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="Figure_3_{y_hist_col}_histogram_data.csv">Download Raw Figure 3 Data</a>'
    st.sidebar.write(href, unsafe_allow_html=True)

    
with middle_middle:
    fig_hist_x = px.histogram(df_selection, x=x_hist_col, nbins=20)
    fig_hist_x.update_layout(
        title_text=f"Figure 4: Histogram of {x_hist_col}",
        title_x=0.5,  # center the title
        margin=dict(t=50)  # add some space at the top
    )
    st.plotly_chart(fig_hist_x)
 # Add download button for exporting raw data from the heatmap
    heatmap_data = df_selection[[x_heatmap_col, y_heatmap_col]]
    csv = heatmap_data.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="Figure_4_{x_hist_col}_{y_hist_col}.csv">Download Raw Figure 4 Data</a>'
    st.sidebar.write(href, unsafe_allow_html=True)

# Statistics Table
with bottom_left:
    st.markdown("<h3><u><b>Summary Statistics</b></u></h3>", unsafe_allow_html=True)
    st.write(df_selection.describe())