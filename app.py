import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import numpy as np

# Dodanie obsługi osadzania w iframe
st.markdown(
  “”"
  <script>
    document.addEventListener(“DOMContentLoaded”, function() {
      let meta = document.createElement(‘meta’);
      meta.httpEquiv = “Content-Security-Policy”;
      meta.content = “frame-ancestors ‘self’ *“;
      document.head.appendChild(meta);
    });
  </script>
  “”",
  unsafe_allow_html=True
)


# Połączenie z bazą danych SQLite
DB_PATH = 'db_heart_disease.db'
conn = sqlite3.connect(DB_PATH)

# Wczytanie danych z tabeli tbl_observations
query = "SELECT * FROM tbl_observations"
query_historical = "SELECT * FROM tbl_observations_historic"
df = pd.read_sql_query(query, conn)
df_historical = pd.read_sql_query(query_historical, conn)

# Zamknięcie połączenia z bazą danych
conn.close()

# Zamień 'NA' na NaN
pd.set_option('future.no_silent_downcasting', True)
df.replace('NA', np.nan, inplace=True)
columns_to_fill = ['currentSmoker', 'cigsPerDay', 'BPMeds', 'prevalentStroke', 'prevalentHyp', 'diabetes']
df[columns_to_fill] = df[columns_to_fill].fillna(0)
df['education']=df['education'].fillna(1)
df['TenYearCHD'] = df['TenYearCHD'].astype(str)
df['currentSmoker'] = df['currentSmoker'].astype(str)
df = df.dropna()

# Możesz zrobić to dla wszystkich kolumn numerycznych
num_cols = ["cigsPerDay", "totChol", "sysBP", "diaBP", "BMI", "heartRate", "glucose","BPMeds","education","diabetes"]
df[num_cols] = df[num_cols].apply(pd.to_numeric, errors='coerce')






# Tytuł aplikacji
st.markdown(
    "<h1 style='color: purple;'>Aplikacja Random Forest Rangers</h1>",
    unsafe_allow_html=True
)

# Dodanie grafiki
st.sidebar.image("logo2.png", use_container_width=True)

# Zakładki
tab1, tab2, tab3, tab4 = st.tabs(["Główna", "Dane", "Dashboard", "Kontakt"])

# Zakładka 1: Główna
with tab1:
    st.header("Witaj w aplikacji!")
    st.write("To jest aplikacja zespołu Random Forest Rangers.")

# Zakładka 2: Dane
with tab2:
    st.header("Dane z bazy danych SQLite")
    st.write("Poniżej znajduje się tabela z aktualnymi danymi z bazy danych:")
    st.dataframe(df)
    st.write(" ")
    st.write("Poniżej znajduje się tabela z historycznymi danymi z bazy danych:")
    st.dataframe(df_historical)
    st.write(" ")
    st.write("Opis pól w zbiorze danych")
    field_descriptions = {
        "male": "Zmienna wskazuje płeć uczestnika. Wartość **1** oznacza mężczyznę, a **0** kobietę.",
        "age": "Wiek uczestnika w latach.",
        "education": "Poziom wykształcenia uczestnika, zapisywany jako kategoria (**0**-podstawowe, **1**-srednie, **2**-wyzsze, **3**-doktorat).",
        "currentSmoker": "Informacja, czy uczestnik jest obecnie palaczem. **1** oznacza, że pali, a **0** – że nie.",
        "cigsPerDay": "Liczba papierosów palonych dziennie przez uczestnika. Może być pusta (dla niepalących).",
        "BPMeds": "Informacja, czy uczestnik przyjmuje leki na nadciśnienie (**Blood Pressure Medications**). **1** oznacza, że przyjmuje, a **0** – że nie.",
        "prevalentStroke": "Informacja o historii udaru mózgu. **1** oznacza, że uczestnik przeszedł udar, a **0** – że nie.",
        "prevalentHyp": "Informacja o nadciśnieniu tętniczym w przeszłości. **1** oznacza, że występowało, a **0** – że nie.",
        "diabetes": "Informacja, czy uczestnik choruje na cukrzycę. **1** oznacza cukrzycę, a **0** – brak.",
        "totChol": "Całkowity poziom cholesterolu w mg/dL.",
        "sysBP": "Skurczowe ciśnienie tętnicze (**systolic blood pressure**) w mmHg.",
        "diaBP": "Rozkurczowe ciśnienie tętnicze (**diastolic blood pressure**) w mmHg.",
        "BMI": "Wskaźnik masy ciała (**Body Mass Index**), który odnosi się do masy ciała w stosunku do wzrostu.",
        "heartRate": "Tętno uczestnika (liczba uderzeń serca na minutę).",
        "glucose": "Poziom glukozy we krwi (mg/dL).",
        "TenYearCHD": "Zmienna wynikowa (**target**). Wskazuje, czy uczestnik miał chorobę niedokrwienną serca (**coronary heart disease**) w ciągu 10 lat. **1** oznacza, że tak, a **0** – że nie."
    }

    for field, description in field_descriptions.items():
        st.markdown(f"**{field}**: {description}")


# Zakładka 3: Dashboard
with tab3:
    st.header("Dashboard")

    # Filtry
    st.sidebar.header("Filtry")

    # Filtr płci
    gender_filter = st.sidebar.selectbox(
        "Płeć",
        options=['Wszyscy', 'Mężczyźni', 'Kobiety'],
        index=0
    )

    # Filtr wieku
    age_range = st.sidebar.slider(
        "Wiek",
        min_value=int(df['age'].min()),
        max_value=int(df['age'].max()),
        value=(int(df['age'].min()), int(df['age'].max())),
        format="%d lat",  # Formatowanie wyświetlania wartości
    )

    # Filtr liczby papierosów dziennie
    cigs_per_day_range = st.sidebar.slider(
        "Liczba papierosów dziennie",
        min_value=int(df['cigsPerDay'].min()),
        max_value=int(df['cigsPerDay'].max()),
        value=(int(df['cigsPerDay'].min()), int(df['cigsPerDay'].max())),
        format="%d szt.",  # Formatowanie wyświetlania wartości
    )

    # Filtr poziomu wykształcenia (multiselect)
    education_options = {
        'Podstawowe': 1,
        'Średnie': 2,
        'Wyższe': 3,
        'Doktorat': 4
    }
    education_filter = st.sidebar.multiselect(
        "Poziom wykształcenia",
        options=list(education_options.keys()),
        default=list(education_options.keys())  # Domyślnie wszystkie opcje wybrane
    )


    # Filtr leków na nadciśnienie
    bp_meds_filter = st.sidebar.selectbox(
        "Leki na nadciśnienie",
        options=['Wszyscy', 'Tak', 'Nie'],
        index=0
    )

    # Filtr historii udaru
    stroke_filter = st.sidebar.selectbox(
        "Historia udaru",
        options=['Wszyscy', 'Tak', 'Nie'],
        index=0
    )

    # Filtr nadciśnienia tętniczego
    hyp_filter = st.sidebar.selectbox(
        "Nadciśnienie tętnicze",
        options=['Wszyscy', 'Tak', 'Nie'],
        index=0
    )

    # Filtr cukrzycy
    diabetes_filter = st.sidebar.selectbox(
        "Cukrzyca",
        options=['Wszyscy', 'Tak', 'Nie'],
        index=0
    )

   # Filtr cholesterolu

    chol_range = st.sidebar.slider(
        "Poziom cholesterolu",
        min_value=int(df['totChol'].min()),
        max_value=int(df['totChol'].max()),
        value=(int(df['totChol'].min()), int(df['totChol'].max())),
        format="%d mg/dL",  # Formatowanie wyświetlania wartości
    )

    # Filtr skurczowego ciśnienia tętniczego
    sys_bp_range = st.sidebar.slider(
        "Skurczowe ciśnienie tętnicze (mmHg)",
        min_value=int(df['sysBP'].min()),
        max_value=int(df['sysBP'].max()),
        value=(int(df['sysBP'].min()), int(df['sysBP'].max())),
        format="%d mmHg",  # Formatowanie wyświetlania wartości
    )

    # Filtr rozkurczowego ciśnienia tętniczego
    dia_bp_range = st.sidebar.slider(
        "Rozkurczowe ciśnienie tętnicze (mmHg)",
        min_value=int(df['diaBP'].min()),
        max_value=int(df['diaBP'].max()+1),
        value=(int(df['diaBP'].min()), int(df['diaBP'].max()+1)),
        format="%d mmHg",  # Formatowanie wyświetlania wartości
    )

    # Filtr BMI
    bmi_range = st.sidebar.slider(
        "BMI",
        min_value=float(df['BMI'].min()),
        max_value=float(df['BMI'].max()),
        value=(float(df['BMI'].min()), float(df['BMI'].max())),
        format="%.1f",  # Formatowanie wyświetlania wartości
    )

    # Filtr tętna
    heart_rate_range = st.sidebar.slider(
        "Tętno (uderzenia/min)",
        min_value=int(df['heartRate'].min()),
        max_value=int(df['heartRate'].max()),
        value=(int(df['heartRate'].min()), int(df['heartRate'].max())),
        format="%d bpm",  # Formatowanie wyświetlania wartości
    )

    # Filtr poziomu glukozy
    glucose_range = st.sidebar.slider(
        "Poziom glukozy (mg/dL)",
        min_value=int(df['glucose'].min()),
        max_value=int(df['glucose'].max()),
        value=(int(df['glucose'].min()), int(df['glucose'].max())),
        format="%d mg/dL",  # Formatowanie wyświetlania wartości
    )
 
    # Filtrowanie danych
    filtered_df = df[
        (df['age'] >= age_range[0]) & (df['age'] <= age_range[1]) &
        (df['totChol'] >= chol_range[0]) & (df['totChol'] <= chol_range[1]) &
        (df['cigsPerDay'] >= cigs_per_day_range[0]) & (df['cigsPerDay'] <= cigs_per_day_range[1]) &
        (df['sysBP'] >= sys_bp_range[0]) & (df['sysBP'] <= sys_bp_range[1]) &
        (df['diaBP'] >= dia_bp_range[0]) & (df['diaBP'] <= dia_bp_range[1]) &
        (df['BMI'] >= bmi_range[0]) & (df['BMI'] <= bmi_range[1]) &
        (df['heartRate'] >= heart_rate_range[0]) & (df['heartRate'] <= heart_rate_range[1]) &
        (df['glucose'] >= glucose_range[0]) & (df['glucose'] <= glucose_range[1])
    ]

    if gender_filter == 'Mężczyźni':
        filtered_df = filtered_df[filtered_df['male'] == 1]
    elif gender_filter == 'Kobiety':
        filtered_df = filtered_df[filtered_df['male'] == 0]

    # Filtrowanie poziomu wykształcenia (multiselect)
    if education_filter:  # Jeśli wybrano jakieś opcje
        education_values = [education_options[edu] for edu in education_filter]
        filtered_df = filtered_df[filtered_df['education'].isin(education_values)]

    if bp_meds_filter == 'Tak':
        filtered_df = filtered_df[filtered_df['BPMeds'] == 1]
    elif bp_meds_filter == 'Nie':
        filtered_df = filtered_df[filtered_df['BPMeds'] == 0]

    if stroke_filter == 'Tak':
        filtered_df = filtered_df[filtered_df['prevalentStroke'] == 1]
    elif stroke_filter == 'Nie':
        filtered_df = filtered_df[filtered_df['prevalentStroke'] == 0]

    if hyp_filter == 'Tak':
        filtered_df = filtered_df[filtered_df['prevalentHyp'] == 1]
    elif hyp_filter == 'Nie':
        filtered_df = filtered_df[filtered_df['prevalentHyp'] == 0]

    if diabetes_filter == 'Tak':
        filtered_df = filtered_df[filtered_df['diabetes'] == 1]
    elif diabetes_filter == 'Nie':
        filtered_df = filtered_df[filtered_df['diabetes'] == 0]

    # Wyświetlenie liczby wybranych rekordów
    st.metric("Liczba wybranych rekordów", len(filtered_df))
    # Wyświetlenie przefiltrowanych danych
    st.write(filtered_df)

    # Dodanie stylu CSS do zmiany koloru suwaków na Purple
    st.markdown(
        """
        <style>
        .stSlider>div>div>div>div {
            background: purple;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    # Wykres 1: Rozkład wieku a poziom cholesterolu
    st.subheader("Rozkład wieku a poziom cholesterolu")
    fig1 = px.scatter(
        filtered_df,
        x='age',
        y='totChol',
        color='TenYearCHD',
        labels={'age': 'Wiek', 'totChol': 'Cholesterol (mg/dL)','TenYearCHD': 'Choroba serca (1 = Chory, 0 = Zdrowy)'},
        color_discrete_map={
            "0": '#D8BFD8',  # Jasnofioletowy (Thistle)
            "1": '#8A2BE2'   # Czerwony
        }
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Wykres 2: Liczba osób z chorobą serca w zależności od płci
    st.subheader("Liczba osób z chorobą serca w zależności od płci")
    fig2 = px.bar(
        filtered_df.groupby(['male', 'TenYearCHD']).size().reset_index(name='count'),
        x='male',
        y='count',
        color='TenYearCHD',
        labels={'male': 'Płeć (1 = Mężczyzna, 0 = Kobieta)', 'count': 'Liczba osób','TenYearCHD': 'Choroba serca (1 = Chory, 0 = Zdrowy)'},
        color_discrete_map={
            "0": '#D8BFD8',  # Jasnofioletowy (Thistle)
            "1": '#8A2BE2'   # Czerwony
        }
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Wykres 3: Rozkład BMI
    st.subheader("Rozkład BMI")
    fig3 = px.histogram(
        filtered_df,
        x='BMI',
        nbins=40,
        barmode='overlay',
        color='TenYearCHD',
        labels={'BMI': 'Wskaźnik masy ciała','TenYearCHD': 'Choroba serca (1 = Chory, 0 = Zdrowy)'},
        color_discrete_map={
            "0": '#D8BFD8',  # Jasnofioletowy (Thistle)
            "1": '#8A2BE2'   # Czerwony
        }
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Wykres 4: Rozkład tętna
    st.subheader("Rozkład tętna")
    fig4 = px.histogram(
        filtered_df,
        x='heartRate',
        nbins=40,
        barmode='overlay',
        color='TenYearCHD',
        labels={'heartRate': 'Tętno (uderzenia/min)','TenYearCHD': 'Choroba serca (1 = Chory, 0 = Zdrowy)'},
        color_discrete_map={
            "0": '#D8BFD8',  # Jasnofioletowy (Thistle)
            "1": '#8A2BE2'   # Czerwony
        }
    )
    st.plotly_chart(fig4, use_container_width=True)

    # Wykres 5: Rozkład cholesterolu
    st.subheader("Rozkład cholesterolu")
    fig5 = px.histogram(
        filtered_df,
        x='totChol',
        nbins=40,
        barmode='overlay',
        color='TenYearCHD',
        labels={'totChol': 'Cholesterol (mg/dL)','TenYearCHD': 'Choroba serca (1 = Chory, 0 = Zdrowy)'},
        color_discrete_map={
            "0": '#D8BFD8',  # Jasnofioletowy (Thistle)
            "1": '#8A2BE2'   # Czerwony
        }
    )
    st.plotly_chart(fig5, use_container_width=True)


    # Tworzymy nową kolumnę łączącą status palacza i chorobę serca
    filtered_df['Smoker_CHD'] = filtered_df.apply(
    lambda row: 
        "Zdrowy i Palący" if row['currentSmoker'] == "1" and row['TenYearCHD'] == "0" else
        "Chory i Palący" if row['currentSmoker'] == "1" and row['TenYearCHD'] == "1" else
        "Zdrowy i Niepalący" if row['currentSmoker'] == "0" and row['TenYearCHD'] == "0" else
        "Chory i Niepalący",
    axis=1
    )

    # Wykres 6: Wpływ palenia na poziom cholesterolu i tętno
    st.subheader("Wpływ palenia na poziom cholesterolu i tętno")

    # Definiowanie mapowania kolorów dla 4 kombinacji
    color_map = {
        'Zdrowy i Niepalący': '#8FBC8F',  
        'Zdrowy i Palący': '#D8BFD8',     
        'Chory i Niepalący': '#FF69B4',   
        'Chory i Palący': '#8A2BE2'      
    }

    # Tworzenie wykresu
    fig6 = px.scatter(
        filtered_df, 
        x="totChol", 
        y="heartRate", 
        color="Smoker_CHD",  # Używamy nowej kolumny 'status' do kolorowania
        labels={
            'totChol': 'Poziom cholesterolu (mg/dL)', 
            'heartRate': 'Tętno (uderzenia na minutę)', 
            'Smoker_CHD': 'Status'
        },
            color_discrete_map=color_map,

    )

    # Wyświetlenie wykresu
    st.plotly_chart(fig6, use_container_width=True)



    # Wykres 7: Wykres pudełkowy dla BMI w zależności od płci i choroby serca
    st.subheader("Rozkład BMI w zależności od płci i choroby serca")

    # Tworzenie wykresu pudełkowego
    fig7 = px.box(
        filtered_df,
        x='male',
        y='BMI',
        color='TenYearCHD',
        labels={
            'male': 'Płeć (1 = Mężczyzna, 0 = Kobieta)',
            'BMI': 'Wskaźnik masy ciała',
            'TenYearCHD': 'Choroba serca (1 = Chory, 0 = Zdrowy)'
        },
        color_discrete_map={
            "0": '#D8BFD8',  # Jasnofioletowy (Thistle)
            "1": '#8A2BE2'   # Czerwony
        }
    )

    # Wyświetlenie wykresu
    st.plotly_chart(fig7, use_container_width=True)

    # Wykres 8: Heatmapa korelacji
    st.subheader("Heatmapa korelacji między zmiennymi")

    # Obliczenie macierzy korelacji
    corr = filtered_df.drop(columns='Smoker_CHD').corr()
    

    # Tworzenie interaktywnej heatmapy za pomocą Plotly
    fig8 = px.imshow(
        corr,
        text_auto=True, 
        color_continuous_scale='RdPu',  
        labels=dict(x="Zmienna1", y="Zmienna2", color="Korelacja"),  
        x=corr.columns,  
        y=corr.columns   
    )

    # Dostosowanie layoutu
    fig8.update_layout(
        xaxis_title="Zmienne",
        yaxis_title="Zmienne",
    )

    # Wyświetlenie wykresu
    st.plotly_chart(fig8, use_container_width=True)
    
# Zakładka 4: Kontakt
with tab4:
    
    st.header("Kontakt")
    st.write("Skontaktuj się z nami!")
    st.write("**Piotr Miernik,  Slawomir Grzybek**")
    st.write("**Marcin Roszak,  Marcin Szumniak**")
    st.write(" ")
    st.write("**Email:** randomforestrangers@example.com")
    st.write("**Telefon:** +48 123 456 789")
    st.write("**Adres:** ul. Data Science 123, 00-001 Warszawa")
    st.image("logo.png", caption="Zespół Random Forest Rangers", width=300)
   
