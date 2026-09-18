%%writefile app.py
import io
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Data Doctor", page_icon="🩺")

st.title("🩺 Data Doctor")
st.write("Ανέβασε ένα Excel ή CSV αρχείο και καθάρισέ το αυτόματα!")

uploaded_file = st.file_uploader(
    "Επίλεξε αρχείο", type=["csv", "xlsx", "xls"]
)

if uploaded_file is not None:
  if uploaded_file.name.endswith(".csv"):
    df = pd.read_csv(uploaded_file)
  else:
    df = pd.read_excel(uploaded_file)

  st.write("###  Αρχικά Δεδομένα")
  st.dataframe(df.head())

  st.write("###  Επιλογές")
  clean_spaces = st.checkbox("Αφαίρεση περιττών κενών (Trim)", value=True)
  drop_dupes = st.checkbox("Αφαίρεση διπλότυπων γραμμών", value=True)
  drop_empty = st.checkbox("Διαγραφή εντελώς κενών γραμμών", value=True)

  if st.button(" Καθαρισμός Τώρα"):
    clean_df = df.copy()

    if clean_spaces:
      for col in clean_df.select_dtypes(include="object").columns:
        clean_df[col] = clean_df[col].astype(str).str.strip()

    if drop_empty:
      clean_df = clean_df.dropna(how="all")

    if drop_dupes:
      clean_df = clean_df.drop_duplicates()

    st.success(
        f"Έτοιμο! Διαγράφηκαν {df.shape[0] - clean_df.shape[0]} περιττές"
        " γραμμές."
    )
    st.dataframe(clean_df.head())

    # Εξαγωγή σε Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
      clean_df.to_excel(writer, index=False)
    processed_data = output.getvalue()

    st.download_button(
        label=" Λήψη Καθαρού Excel",
        data=processed_data,
        file_name="cleaned_data.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
    )
