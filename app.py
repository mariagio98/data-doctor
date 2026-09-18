import io
import re
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Data Doctor", page_icon="🩺", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #f7f9fc 0%, #eef2f8 100%);
    }

    /* Hero header */
    .hero {
        background: linear-gradient(135deg, #4f8bf9 0%, #6ee7d8 100%);
        padding: 2.2rem 2rem;
        border-radius: 18px;
        margin-bottom: 1.8rem;
        box-shadow: 0 8px 24px rgba(79, 139, 249, 0.25);
    }
    .hero h1 {
        color: white;
        font-size: 2.1rem;
        margin: 0 0 0.3rem 0;
    }
    .hero p {
        color: rgba(255,255,255,0.92);
        font-size: 1.05rem;
        margin: 0;
    }

    /* Section cards */
    .card {
        background: white;
        border-radius: 14px;
        padding: 1.3rem 1.5rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 2px 10px rgba(20, 30, 60, 0.06);
        border: 1px solid #eef0f5;
    }
    .card h3 {
        margin-top: 0;
    }

    /* Buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #4f8bf9, #3f6fd6);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.4rem;
        font-weight: 600;
        font-size: 1rem;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        box-shadow: 0 4px 12px rgba(79, 139, 249, 0.35);
    }
    div.stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(79, 139, 249, 0.45);
    }

    div.stDownloadButton > button {
        background: linear-gradient(135deg, #34c98f, #22a878);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(52, 201, 143, 0.35);
    }
    div.stDownloadButton > button:hover {
        transform: translateY(-1px);
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background: #f7f9fc;
        border-radius: 12px;
        padding: 0.6rem 0.8rem;
        border: 1px solid #eef0f5;
    }

    /* File uploader */
    section[data-testid="stFileUploaderDropzone"] {
        border-radius: 14px;
        border: 2px dashed #4f8bf9 !important;
    }

    footer {visibility: hidden;}
    </style>

    <div class="hero">
        <h1>🩺 Data Doctor</h1>
        <p>Ανέβασε ένα Excel ή CSV αρχείο και καθάρισέ το αυτόματα, με λίγα κλικ.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "📁 Επίλεξε αρχείο (CSV, XLSX, XLS)", type=["csv", "xlsx", "xls"]
)


def clean_column_names(columns):
    """Trim, lowercase, αντικατάσταση κενών/ειδικών χαρακτήρων με underscore."""
    new_cols = []
    for col in columns:
        c = str(col).strip().lower()
        c = re.sub(r"\s+", "_", c)
        c = re.sub(r"[^\w]", "", c)
        new_cols.append(c)
    return new_cols


def remove_special_chars(series):
    return series.astype(str).str.replace(r"[^\w\s]", "", regex=True)


if uploaded_file is not None:
    # --- Ανάγνωση αρχείου (με επιλογή φύλλου αν είναι Excel με πολλά sheets) ---
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        xls = pd.ExcelFile(uploaded_file)
        if len(xls.sheet_names) > 1:
            sheet = st.selectbox("Επίλεξε φύλλο (sheet)", xls.sheet_names)
        else:
            sheet = xls.sheet_names[0]
        df = pd.read_excel(xls, sheet_name=sheet)

    with st.container(border=True):
        st.write("#### 📋 Αρχικά Δεδομένα")
        st.dataframe(df.head(), use_container_width=True)

        col1, col2, col3 = st.columns(3)
        col1.metric("Γραμμές", df.shape[0])
        col2.metric("Στήλες", df.shape[1])
        col3.metric("Κενές τιμές (σύνολο)", int(df.isna().sum().sum()))

        with st.expander("📊 Περισσότερα στατιστικά ανά στήλη"):
            stats_df = pd.DataFrame({
                "Τύπος": df.dtypes.astype(str),
                "Κενές τιμές": df.isna().sum(),
                "% Κενών": (df.isna().mean() * 100).round(1),
            })
            st.dataframe(stats_df, use_container_width=True)

    with st.container(border=True):
        st.write("#### ⚙️ Επιλογές Καθαρισμού")

        st.markdown("**Βασικός καθαρισμός**")
        c1, c2 = st.columns(2)
        with c1:
            clean_spaces = st.checkbox("Αφαίρεση περιττών κενών (Trim)", value=True)
            drop_dupes = st.checkbox("Αφαίρεση διπλότυπων γραμμών", value=True)
            drop_empty_rows = st.checkbox("Διαγραφή εντελώς κενών γραμμών", value=True)
            drop_empty_cols = st.checkbox("Διαγραφή εντελώς κενών στηλών", value=False)
        with c2:
            clean_headers = st.checkbox("Καθαρισμός ονομάτων στηλών (πεζά, underscores)", value=False)
            drop_dupe_cols = st.checkbox("Αφαίρεση διπλότυπων στηλών", value=False)
            strip_special = st.checkbox("Αφαίρεση ειδικών χαρακτήρων από κείμενο", value=False)

        st.divider()
        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown("**Κείμενο**")
            text_case = st.selectbox(
                "Μορφή κειμένου (για στήλες με text)",
                ["Καμία αλλαγή", "πεζά (lower)", "ΚΕΦΑΛΑΙΑ (upper)", "Πρώτο Γράμμα Κεφαλαίο (title)"],
            )
        with col_right:
            st.markdown("**Κενές τιμές (NaN)**")
            fill_method = st.selectbox(
                "Συμπλήρωση κενών τιμών",
                ["Καμία", "Με 0 (αριθμητικές)", "Με μέσο όρο (mean)", "Με διάμεσο (median)",
                 "Με συχνότερη τιμή (mode)", "Με προσαρμοσμένο κείμενο"],
            )
            custom_fill_value = ""
            if fill_method == "Με προσαρμοσμένο κείμενο":
                custom_fill_value = st.text_input("Τιμή συμπλήρωσης", value="")

        st.write("")
        clean_clicked = st.button("🧹 Καθαρισμός Τώρα", use_container_width=True)

    if clean_clicked:
        clean_df = df.copy()
        actions_log = []

        if clean_headers:
            clean_df.columns = clean_column_names(clean_df.columns)
            actions_log.append("Καθαρίστηκαν τα ονόματα των στηλών.")

        if clean_spaces:
            for col in clean_df.select_dtypes(include="object").columns:
                clean_df[col] = clean_df[col].astype(str).str.strip()
            actions_log.append("Αφαιρέθηκαν τα περιττά κενά.")

        if strip_special:
            for col in clean_df.select_dtypes(include="object").columns:
                clean_df[col] = remove_special_chars(clean_df[col])
            actions_log.append("Αφαιρέθηκαν ειδικοί χαρακτήρες από το κείμενο.")

        if text_case != "Καμία αλλαγή":
            text_cols = clean_df.select_dtypes(include="object").columns
            for col in text_cols:
                if text_case == "πεζά (lower)":
                    clean_df[col] = clean_df[col].astype(str).str.lower()
                elif text_case == "ΚΕΦΑΛΑΙΑ (upper)":
                    clean_df[col] = clean_df[col].astype(str).str.upper()
                elif text_case == "Πρώτο Γράμμα Κεφαλαίο (title)":
                    clean_df[col] = clean_df[col].astype(str).str.title()
            actions_log.append(f"Εφαρμόστηκε μορφή κειμένου: {text_case}.")

        if fill_method != "Καμία":
            if fill_method == "Με 0 (αριθμητικές)":
                num_cols = clean_df.select_dtypes(include="number").columns
                clean_df[num_cols] = clean_df[num_cols].fillna(0)
            elif fill_method == "Με μέσο όρο (mean)":
                num_cols = clean_df.select_dtypes(include="number").columns
                clean_df[num_cols] = clean_df[num_cols].fillna(clean_df[num_cols].mean())
            elif fill_method == "Με διάμεσο (median)":
                num_cols = clean_df.select_dtypes(include="number").columns
                clean_df[num_cols] = clean_df[num_cols].fillna(clean_df[num_cols].median())
            elif fill_method == "Με συχνότερη τιμή (mode)":
                for col in clean_df.columns:
                    mode_vals = clean_df[col].mode(dropna=True)
                    if not mode_vals.empty:
                        clean_df[col] = clean_df[col].fillna(mode_vals.iloc[0])
            elif fill_method == "Με προσαρμοσμένο κείμενο":
                clean_df = clean_df.fillna(custom_fill_value)
            actions_log.append(f"Συμπληρώθηκαν οι κενές τιμές ({fill_method}).")

        if drop_empty_rows:
            before = clean_df.shape[0]
            clean_df = clean_df.dropna(how="all")
            actions_log.append(f"Διαγράφηκαν {before - clean_df.shape[0]} εντελώς κενές γραμμές.")

        if drop_empty_cols:
            before = clean_df.shape[1]
            clean_df = clean_df.dropna(axis=1, how="all")
            actions_log.append(f"Διαγράφηκαν {before - clean_df.shape[1]} εντελώς κενές στήλες.")

        if drop_dupe_cols:
            before = clean_df.shape[1]
            clean_df = clean_df.loc[:, ~clean_df.T.duplicated()]
            actions_log.append(f"Διαγράφηκαν {before - clean_df.shape[1]} διπλότυπες στήλες.")

        if drop_dupes:
            before = clean_df.shape[0]
            clean_df = clean_df.drop_duplicates()
            actions_log.append(f"Διαγράφηκαν {before - clean_df.shape[0]} διπλότυπες γραμμές.")

        with st.container(border=True):
            st.success(
                f"✅ Έτοιμο! Οι γραμμές μειώθηκαν από {df.shape[0]} σε {clean_df.shape[0]}, "
                f"οι στήλες από {df.shape[1]} σε {clean_df.shape[1]}."
            )

            if actions_log:
                with st.expander("📝 Τι έγινε ακριβώς", expanded=False):
                    for a in actions_log:
                        st.write(f"- {a}")

            st.write("#### ✨ Καθαρά Δεδομένα")
            st.dataframe(clean_df.head(20), use_container_width=True)

            # --- Εξαγωγή σε Excel ---
            output_excel = io.BytesIO()
            with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
                clean_df.to_excel(writer, index=False)
            excel_data = output_excel.getvalue()

            # --- Εξαγωγή σε CSV ---
            csv_data = clean_df.to_csv(index=False).encode("utf-8-sig")

            st.write("")
            col_a, col_b = st.columns(2)
            with col_a:
                st.download_button(
                    label="⬇️ Λήψη Excel",
                    data=excel_data,
                    file_name="cleaned_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
            with col_b:
                st.download_button(
                    label="⬇️ Λήψη CSV",
                    data=csv_data,
                    file_name="cleaned_data.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
else:
    st.markdown(
        """
        <div class="card" style="text-align:center; color:#6b7280;">
            📂 Ανέβασε ένα αρχείο για να ξεκινήσεις.
        </div>
        """,
        unsafe_allow_html=True,
    )
