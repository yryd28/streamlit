import pandas as pd
import altair as alt
import streamlit as st

st.set_page_config(layout="wide")

original_df = pd.read_csv('https://docs.google.com/spreadsheets/d/15J3TSC3pW7378tVSZBLqDhAjqOxBGk22uw4J9qx_63M/export?gid=1428763389&format=csv', header=0)
df = original_df.copy()

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# INTERFACE
# Row 1: Header & Filter
row1col1, row1col2 = st.columns([3, 1])

with row1col1:
    st.markdown("""
    <style>
    .big-font {
        font-size:60px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    st.markdown('<p class="big-font">Jemaat HKBP Depok 1 </p>', unsafe_allow_html=True)

with row1col2:
    wijk_list = ["Semua WIJK", "Efesus", "Gesemane", "Betlehem", "Judea", "Kapernaum", "Laodekia", "Kolose", "Jeriko", "Antiokia", "Jordan", "Philadelfia", "Galilea"]
    wijk = st.selectbox(
        label="WIJK",
        options=(wijk_list)
    )

def filter(wijk):
    if wijk == "Semua WIJK":
        return original_df
    else:
        return df[df["WIJK"] == wijk.upper()]
df = filter(wijk)


# CLEANING
# Hapus data yang tidak valid
df = df[(df['NAMA KEPALA KELUARGA /AMA'] != 'ANTON THE') & (df['NAMA KEPALA KELUARGA /AMA'] != 'Tes')]

# Hapus data duplikat
df = df.drop_duplicates(subset=["NAMA KEPALA KELUARGA /AMA"], keep="first")

# Hapus kolom yang tidak penting
unimportant_columns = ["No", "Timestamp", "NIR"]
for column in df.columns:
  if column.startswith("NOMOR") or column.startswith("ALAMAT") or (column.startswith("STATUS") and "TINGGAL" in column):
    unimportant_columns.append(column)

df.drop(columns=unimportant_columns, inplace=True)

# Ganti tipe data
date_columns = [column for column in df.columns if column.startswith("TANGGA") and "BAPTIS.6" not in column]
df[date_columns] = df[date_columns].applymap(
    lambda x: pd.to_datetime(x, format="%d/%m/%Y") if pd.notna(x) and int(x[-4:]) >= 1900 else pd.NaT
)

# Tambah kolom
tanggal_lahir = [column for column in df.columns if "TANGGAL LAHIR" in column]

today = pd.Timestamp.now()
for tanggal in tanggal_lahir:
  umur_column = tanggal.replace("TANGGAL LAHIR", "UMUR")
  df[umur_column] = (today - df[tanggal]).dt.days // 365.25

# Interpolasi data
df.loc[~df["NAMA ISTRI/INA"].isna(), "JENIS KELAMIN.1"] = "PEREMPUAN"

# Generalisasi kategori
# pendidikan
pendidikan = [column for column in df.columns if "PENDIDIKAN" in column]
df[pendidikan] = df[pendidikan].replace("D3", "D3/D4")

# status perkawinan
kawin = [column for column in df.columns if "KAWIN" in column and not column.endswith(".1")]

df[kawin] = df[kawin].replace(["BELUM KAWIN", "0", "-", "", "Pelajar", "Masih anak anak", "Balita", "Masih Balita", "Masih ank2", "Masih sekolah", "Masih sekolah smp", "Remaja"], "Belum Kawin")
df[kawin] = df[kawin].replace(["KAWIN", "KAWIN ", "06/06/2015"], "Kawin")
df[kawin] = df[kawin].replace(["Cerai", "Cerai hidup"], "Cerai")


# DASHBOARD
# Row 2: Numbers
jemaat = [column for column in df.columns if column.startswith("NAMA") and "SINTUA" not in column]
jemaat_count = sum(df[column].notna().sum() for column in jemaat)

kk = ["NAMA KEPALA KELUARGA /AMA"]
kk_count = sum(df[column].notna().sum() for column in kk)

baptis = [column for column in df.columns if "BAPTIS" in column and not column.endswith("6")]
baptis_count = sum(df[column].notna().sum() for column in baptis)

sidi = [column for column in df.columns if "SIDI" in column]
sidi_count = sum(df[column].notna().sum() for column in sidi)

row2col1, row2col2, row2col3, row2col4 = st.columns((5,5,5,5))
with row2col1:
    st.metric(label="Jemaat", value=jemaat_count)
with row2col2:
    st.metric(label="Keluarga", value=kk_count)
with row2col3:
    st.metric(label="Sudah Baptis", value=baptis_count)
with row2col4:
    st.metric(label="Sudah Sidi", value=sidi_count)

# Row 3: Charts 1
row3col1, row3col2, row3col3= st.columns([4,3,3])

with row3col1:
    wijk_combined = pd.DataFrame()

    for index, row in df.iterrows():
        for anggota in jemaat:
            if anggota == "NAMA KEPALA KELUARGA /AMA":
                wijk_row = df.loc[index, "WIJK"]
            if not pd.isna(df.loc[index, anggota]):
                wijk_combined = pd.concat([wijk_combined, pd.DataFrame([{"WIJK": wijk_row}])], ignore_index=True)

    wijk_chart = alt.Chart(wijk_combined).mark_bar().encode(
        y=alt.Y("count()", sort="-x", title = "Jumlah"),
        x=alt.X("WIJK:N")
    ).properties(
        title="WIJK Jemaat HKBP Depok 1"
    ).interactive()
    st.altair_chart(    
        wijk_chart, use_container_width=True,
    )
        

with row3col2:
    jenis_kelamin_combined = pd.DataFrame()

    jenis_kelamin = [column for column in df.columns if "JENIS KELAMIN" in column]
    for index, row in df.iterrows():
        for jenis_kelamin_singular in jenis_kelamin:
            if not pd.isna(df.loc[index, jenis_kelamin_singular]):
                jenis_kelamin_combined = pd.concat([jenis_kelamin_combined, pd.DataFrame([{"Jenis Kelamin": df.loc[index, jenis_kelamin_singular]}])], ignore_index=True)

    jenis_kelamin_chart = alt.Chart(jenis_kelamin_combined).mark_arc().encode(
        theta="count()",
        color=alt.Color("Jenis Kelamin:N", scale=alt.Scale(scheme="set1"))
    ).properties(
        title="Jenis Kelamin Jemaat HKBP Depok 1"
    ).interactive()
    jenis_kelamin_chart.configure(background='#0000FF')
    st.altair_chart(
        jenis_kelamin_chart, use_container_width=True
    )

with row3col3:
    goldar_combined = pd.DataFrame()

    goldar = [column for column in df.columns if "DARAH" in column]
    for index, row in df.iterrows():
        for goldar_singular in goldar:
            if not pd.isna(df.loc[index, goldar_singular]):
                goldar_combined = pd.concat([goldar_combined, pd.DataFrame([{"Golongan Darah": df.loc[index, goldar_singular]}])], ignore_index=True)

    goldar_chart = alt.Chart(goldar_combined).mark_bar().encode(
        x=alt.X("count()", title = "Jumlah"),
        y=alt.Y("Golongan Darah:N")
    ).properties(
        title="Golongan Darah Jemaat HKBP Depok 1"
    ).interactive()

    st.altair_chart(
        goldar_chart, use_container_width=True
    )

# Row 4: Charts 2
row4col1, row4col2, row4col3 = st.columns([4,3,3])

with row4col1:
    umur_combined = pd.DataFrame()

    umur = [column for column in df.columns if "UMUR" in column]
    for index, row in df.iterrows():
        for umur_singular in umur:
            if not pd.isna(df.loc[index, umur_singular]):
                umur_combined = pd.concat([umur_combined, pd.DataFrame([{"Umur": df.loc[index, umur_singular]}])], ignore_index=True)

    umur_chart = alt.Chart(umur_combined).mark_bar().encode(
        alt.X("Umur", bin=True, title = "Umur"),
        y=alt.Y("count()", title = "Jumlah")
    ).properties(
        title="Umur Jemaat HKBP Depok 1"
    ).interactive()

    st.altair_chart(
        umur_chart, use_container_width=True
    )


with row4col2:
    pekerjaan_combined = pd.DataFrame()

    pekerjaan = [column for column in df.columns if column.startswith("STATUS") and "PEKERJAAN" in column]
    for index, row in df.iterrows():
        for pekerjaan_singular in pekerjaan:
            if not pd.isna(df.loc[index, pekerjaan_singular]):
                pekerjaan_combined = pd.concat([pekerjaan_combined, pd.DataFrame([{"Pekerjaan": df.loc[index, pekerjaan_singular]}])], ignore_index=True)

    pekerjaan_chart = alt.Chart(pekerjaan_combined).mark_arc(innerRadius=50).encode(
        theta="count()",
        color=alt.Color("Pekerjaan:N", scale=alt.Scale(scheme="set1"))
    ).properties(
        title="Pekerjaan Jemaat HKBP Depok 1"
    ).interactive()

    st.altair_chart(
        pekerjaan_chart, use_container_width=True
    )

with row4col3:
    pendidikan_combined = pd.DataFrame()

    for index, row in df.iterrows():
        for pendidikan_singular in pendidikan:
            if not pd.isna(df.loc[index, pendidikan_singular]):
                pendidikan_combined = pd.concat([pendidikan_combined, pd.DataFrame([{"Pendidikan": df.loc[index, pendidikan_singular]}])], ignore_index=True)

    pendidikan_chart = alt.Chart(pendidikan_combined).mark_bar().encode(
        y=alt.Y("count()", sort="-x", title = "Jumlah"),
        x=alt.X("Pendidikan:N")
    ).properties(
        title="Pendidikan Jemaat HKBP Depok 1"
    ).interactive()

    st.altair_chart(
        pendidikan_chart, use_container_width=True
    )
