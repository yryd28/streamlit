import streamlit as st 
import numpy as np
import pandas as pd
import plotly.express as px

df = pd.read_csv("https://docs.google.com/spreadsheets/d/1Z0_67Uq_SYDnxktoAojXXtEqFpumSFyP_d6P_YI_fjA/export?gid=1847785796&format=csv", header=0)

st.set_page_config(
    page_title = 'Real-Time Dashboard',
    layout = 'wide'
)

#with open('style.css') as f:
    #st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.title("Real-Time HKBP Dashboard")

WIJK_filter = st.selectbox("WIJK: ", pd.unique(df['WIJK']))
#placeholder = st.empty()
dfw = df[df['WIJK']==WIJK_filter]

date_columns = [column for column in df.columns if column.startswith("TANGGA") and "BAPTIS.6" not in column]
df[date_columns] = df[date_columns].applymap(
    lambda x: pd.to_datetime(x, format="%d/%m/%Y") if pd.notna(x) and int(x[-4:]) >= 1900 else pd.NaT
)
tanggal_lahir = [column for column in df.columns if "TANGGAL LAHIR" in column]
today = pd.Timestamp.now()
for tanggal in tanggal_lahir:
  umur_column = tanggal.replace("TANGGAL LAHIR", "UMUR")
  df[umur_column] = (today - df[tanggal]).dt.days // 365.25

jemaat = [column for column in df.columns if column.startswith("NAMA") and "SINTUA" not in column]
Total_jemaat = sum(df[column].notna().sum() for column in jemaat)

#with placeholder.container():
a1, a2, a3 = st.columns(3)
a1.metric(label="Total Jemaat ", value=Total_jemaat)
#a2.metric(label= , value=)
#a3.metric(label= , value=)

#
b1, b2 = st.columns((5,5))
with b1:
   st.markdown('### Bar Chart')
   Bar_data = df["WIJK"].value_counts().sort_values()
   fig = px.bar(x=Bar_data.index, y=Bar_data)
   st.plotly_chart(fig)

with b2:
   st.markdown('### Pie Chart')
   Pie_data = df["JENIS KELAMIN"].value_counts().sort_values()
   fig = px.pie(names=Pie_data, values=Pie_data.index)
   st.plotly_chart(fig)

#
st.markdown('### Scatter Plot')
c1, c2 = st.columns(2)
metric_choice = ["UMUR", "JENIS KELAMIN", "JENIS PEKERJAAN"]
choice1 = c1.selectbox("Horizontal" , options= metric_choice)
choice2 = c2.selectbox("Vertical" , options= metric_choice)
fig = px.scatter(x= choice1,
                 y= choice2,
                 hover_name = 'WIJK',
                 hover_data = ['WIJK'],
                 size = 'view',
                 title =f'Correlation of {choice1.title} and {choice2.title}')
st.plotly_chart(fig)



