import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from azure.cosmos import CosmosClient
import os
from dotenv import load_dotenv

st.set_page_config(layout="wide", page_title="HOPP Analytics")

st.title("🏥 HOPP Asiakaspalaute dashboard")

st.markdown("""
## Tervetuloa HOPPlop-analytiikkatyökaluun!

Tämä työkalu auttaa sinua analysoimaan hoitotyön palautedataa eri yksiköistä. Voit tarkastella trendejä, vertailla yksiköitä ja syventyä yksityiskohtaisiin jakaumiin.

### Käytössä olevat yksiköt:
- **AIKTEHOHO**: Aikuisten tehohoito
- **EALAPSAIK**: Lasten ja nuorten päivystyspoliklinikka
- **ENSIHOITO**: Ensihoitopalvelut

### Tärkeimmät ominaisuudet:
- 📊 Trendinäkymä yksikkövertailuilla
- 🌡️ Lämpökartta kokonaiskuvan hahmottamiseen
- 📈 Yksityiskohtaiset jakaumat kysymyskohtaiseen analyysiin
""")

def sort_quarters(quarters):
    """Järjestää vuosineljännekset oikeaan järjestykseen."""
    if isinstance(quarters, pd.Index):
        quarters = quarters.tolist()
    return sorted(quarters, key=lambda x: (int(x.split('_')[1]), int(x.split('_')[0])))
    
# Data loading
@st.cache_data
def load_data():
    load_dotenv('../../shared/.env')
    
    # Azure Cosmos DB setup
    client = CosmosClient(
        os.getenv('COSMOSDB_ENDPOINT'),
        os.getenv('COSMOSDB_KEY')
    )
    
    database = client.get_database_client('MojovaDB')
    container = database.get_container_client('Analytics')
    
    # Query data
    query = "SELECT * FROM c WHERE c['/medallion'] = 'silver_hopp'"
    items = container.query_items(query=query, enable_cross_partition_query=True)
    data = list(items)
    
    df = pd.DataFrame(data)
    
    

    # Datan siistiminen
    numeric_columns = [col for col in df.columns if col.split('_')[0].isdigit()]
    df[numeric_columns] = df[numeric_columns].replace('E', np.nan)
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')
    
    # Poistetaan NAN-rivit ja korvataan keskiarvoilla
    df.dropna(how="all", subset=numeric_columns, inplace=True)
    df[numeric_columns] = df[numeric_columns].apply(lambda col: col.fillna(col.mean()))
    
    # Luodaan kartoitus kysymyksille
    question_descriptions = {col: col.split('_', 1)[1].replace('_', ' ').capitalize() for col in numeric_columns}
    
    return df, numeric_columns, question_descriptions

def calculate_averages(data, numeric_columns, selected_units):
    """Laskee yksikkö- ja kansalliset keskiarvot."""
    unit_avg = data.groupby(['unit_code', 'quarter'])[numeric_columns].mean()
    national_avg = data.groupby('quarter')[numeric_columns].mean()
    
    # Järjestä vuosineljännekset
    unit_avg = unit_avg.reset_index()
    unit_avg['quarter'] = pd.Categorical(
        unit_avg['quarter'],
        categories=sort_quarters(unit_avg['quarter'].unique()),
        ordered=True
    )
    unit_avg = unit_avg.sort_values('quarter')
    
    national_avg = national_avg.reset_index()
    national_avg['quarter'] = pd.Categorical(
        national_avg['quarter'],
        categories=sort_quarters(national_avg['quarter'].unique()),
        ordered=True
    )
    national_avg = national_avg.sort_values('quarter')
    
    return unit_avg, national_avg

df, numeric_columns, question_descriptions = load_data()
selected_units = ["AIKTEHOHO", "EALAPSAIK", "ENSIHOITO"]
unit_avg, national_avg = calculate_averages(df, numeric_columns, selected_units)

# Välilehdet eri visualisoinneille
tab1, tab2, tab3 = st.tabs(["📊 Trendit", "🌡️ Lämpökartta", "📈 Jakaumat"])

with tab1:
    st.header("Kysymyskohtaiset trendit")
    st.markdown("""
    **Käyttöohje:**
    1. Valitse kysymys pudotusvalikosta nähdäksesi sen kehityksen ajan mittaan
    2. Vertaa eri yksiköiden tuloksia toisiinsa ja kansalliseen keskiarvoon
    3. Vie hiiri datapisteiden päälle nähdäksesi tarkat arvot
    
    *Huom: Kansallinen keskiarvo näkyy mustalla katkoviivalla*
    """)
    
    # Kysymysvalikko
    selected_question = st.selectbox(
        "Valitse kysymys:",
        numeric_columns,
        format_func=lambda x: f"Kysymys {x.split('_')[0]}: {question_descriptions[x]}"
    )
    
    # Interaktiivisen line chartin luonti
    def create_line_race_chart(unit_avg, national_avg, selected_question):
        traces = []
        
        # Kansallinen keskiarvo mustalla katkoviivalla
        traces.append(
            go.Scatter(
                x=national_avg['quarter'], 
                y=national_avg[selected_question], 
                mode='lines+markers',
                name='Kansallinen keskiarvo',
                line=dict(color='black', dash='dot'),
                hovertemplate='Kansallinen: %{y:.2f}<extra></extra>'
            )
        )
        
        # Yksikkökohtaiset viivat
        colors = ['#1f77b4', '#2ca02c', '#d62728']  
        for i, unit in enumerate(selected_units):
            unit_data = unit_avg[unit_avg['unit_code'] == unit]
            traces.append(
                go.Scatter(
                    x=unit_data['quarter'], 
                    y=unit_data[selected_question], 
                    mode='lines+markers',
                    name=unit,
                    line=dict(color=colors[i % len(colors)]),
                    hovertemplate=f'{unit}: %{{y:.2f}}<extra></extra>'
                )
            )
        
        layout = go.Layout(
            title=f"Kysymys {selected_question.split('_')[0]}: {question_descriptions[selected_question]}",
            xaxis=dict(title='Vuosineljännes', tickangle=45),
            yaxis=dict(title='Keskiarvo'),
            hovermode='closest',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        fig = go.Figure(data=traces, layout=layout)
        return fig
    
    st.plotly_chart(create_line_race_chart(unit_avg, national_avg, selected_question), use_container_width=True)

with tab2:
    st.header("Lämpökartta")
    st.markdown("""
    **Käyttöohje:**
    1. Valitse tarkasteltava yksikkö pudotusvalikosta (tai katso kaikkien keskiarvoa)
    2. Tutki väriskaalaa: tummempi sininen = korkeampi arvo
    3. Arvot näkyvät suoraan kartalla, ja tarkemmat tiedot saa viemällä hiiren lukujen päälle
    
    *Lämpökartta auttaa tunnistamaan nopeasti vahvuudet ja kehityskohteet*
    """)
    
    # Yksikön valinta lämpökarttaa varten
    unit_selection = st.selectbox(
        "Valitse yksikkö lämpökarttaan:",
        ["Kaikki", "AIKTEHOHO", "EALAPSAIK", "ENSIHOITO"],
        key="heatmap_unit",
        help="Valitse yksikkö nähdäksesi sen tulokset, tai valitse 'Kaikki' nähdäksesi kaikkien yksiköiden keskiarvon"
    )
    
    # Suodata data valitun yksikön mukaan ja vain halutuille yksiköille
    valid_units = ["AIKTEHOHO", "EALAPSAIK", "ENSIHOITO"]
    filtered_df = df[df['unit_code'].isin(valid_units)]  # Esivalitse vain halutut yksiköt
    
    if unit_selection != "Kaikki":
        filtered_df = filtered_df[filtered_df['unit_code'] == unit_selection]
    
    # Laske keskiarvot lämpökarttaa varten
    grouped_averages = filtered_df.groupby('quarter')[numeric_columns].mean()
    grouped_averages = grouped_averages.reset_index()
    grouped_averages['quarter'] = pd.Categorical(
        grouped_averages['quarter'],
        categories=sort_quarters(grouped_averages['quarter'].unique()),
        ordered=True
    )
    grouped_averages = grouped_averages.sort_values('quarter').set_index('quarter')
    
    # Luo lämpökartta arvoilla
    fig = go.Figure(data=go.Heatmap(
        z=grouped_averages.values,
        x=[f"Q{i.split('_')[0]}: {question_descriptions[i][:30]}..." for i in numeric_columns],
        y=grouped_averages.index,
        colorscale='Blues',
        text=np.round(grouped_averages.values, 2),  # Näytä arvot
        texttemplate="%{text}",  # Käytä pyöristettyjä arvoja
        textfont={"size": 10},
        hoverongaps=False
    ))
    
    fig.update_layout(
        title=f'Kysymysten keskiarvot vuosineljänneksittäin - {unit_selection}',
        xaxis_title='Kysymys',
        yaxis_title='Vuosineljännes',
        height=800
    )
    
    st.plotly_chart(fig, use_container_width=True)


with tab3:
    st.header("Kysymyskohtaiset jakaumat")
    st.markdown("""
    **Käyttöohje:**
    1. Valitse tarkasteltava vuosineljännes
    2. Valitse yksikkö (tai tarkastele kaikkia)
    3. Valitse yksi tai useampi kysymys vertailuun
    
    *Box plot -kuvaajassa:*
    - Laatikko näyttää arvojen keskimmäiset 50%
    - Viiva laatikon sisällä on mediaani
    - Yksittäiset pisteet ovat poikkeavia arvoja
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_quarter = st.selectbox(
            "Valitse vuosineljännes:",
            sort_quarters(df['quarter'].unique())
        )
    
    with col2:
        selected_unit_dist = st.selectbox(
            "Valitse yksikkö:",
            ["Kaikki", "AIKTEHOHO", "EALAPSAIK", "ENSIHOITO"],
            key="distribution_unit"
        )
    
    with col3:
        selected_questions = st.multiselect(
            "Valitse kysymykset vertailuun:",
            numeric_columns,
            default=[numeric_columns[0]],
            format_func=lambda x: f"Q{x.split('_')[0]}: {question_descriptions[x]}"
        )
    
    if selected_questions:
        # Suodata ensin vain halutut yksiköt
        valid_units = ["AIKTEHOHO", "EALAPSAIK", "ENSIHOITO"]
        filtered_df = df[df['unit_code'].isin(valid_units)]
        
        # Suodata sitten vuosineljänneksen mukaan
        filtered_df = filtered_df[filtered_df['quarter'] == selected_quarter]
        
        # Ja lopuksi yksikön mukaan jos ei ole "Kaikki"
        if selected_unit_dist != "Kaikki":
            filtered_df = filtered_df[filtered_df['unit_code'] == selected_unit_dist]
        
        # Box plot
        fig = go.Figure()
        for question in selected_questions:
            fig.add_trace(go.Box(
                y=filtered_df[question],
                name=f"Q{question.split('_')[0]}",
                boxpoints='all',
                jitter=0.3,
                pointpos=-1.8,
                hovertext=[question_descriptions[question]],
            ))
        
        fig.update_layout(
            title=f'Vastausten jakauma - {selected_quarter} - {selected_unit_dist}',
            yaxis_title='Arvot',
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Yleisiä mittaristoja
st.header("📊 Yleiset mittarit")
st.markdown("""
*Nämä mittarit antavat nopean yleiskuvan palautteen tasosta:*
""")

col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_overall = df[numeric_columns].mean().mean()
    st.metric(
        "Keskiarvo (kaikki)", 
        f"{avg_overall:.2f}",
        help="Kaikkien kysymysten ja yksiköiden kokonaiskeskiarvo"
    )

with col2:
    latest_quarter = sort_quarters(df['quarter'].unique())[-1]
    avg_latest = df[df['quarter'] == latest_quarter][numeric_columns].mean().mean()
    st.metric(
        "Viimeisin keskiarvo", 
        f"{avg_latest:.2f}",
        help=f"Keskiarvo viimeisimmältä kaudelta ({latest_quarter})"
    )

with col3:
    best_question = df[numeric_columns].mean().idxmax()
    best_score = df[numeric_columns].mean().max()
    st.metric(
        "Paras kysymys", 
        f"Q{best_question.split('_')[0]}", 
        f"{best_score:.2f}",
        help=f"Parhaiten arvioitu kysymys: {question_descriptions[best_question]}"
    )

with col4:
    needs_improvement = df[numeric_columns].mean().idxmin()
    lowest_score = df[numeric_columns].mean().min()
    st.metric(
        "Kehityskohde", 
        f"Q{needs_improvement.split('_')[0]}", 
        f"{lowest_score:.2f}",
        help=f"Heikoimman arvion saanut kysymys: {question_descriptions[needs_improvement]}"
    )


st.markdown("""
---
### 💡 Vinkkejä datan tulkintaan:
- Tarkastele trendejä pidemmällä aikavälillä yksittäisten arvojen sijaan
- Vertaile yksiköiden tuloksia kansalliseen keskiarvoon
- Kiinnitä huomiota sekä huippuarvoihin että kehityskohteisiin
- Hyödynnä lämpökarttaa kokonaiskuvan hahmottamiseen

*Tarvitsetko apua työkalun käytössä? Ota yhteyttä [tukeen](mailto:support@example.com)*
""")

st.write("### Kaikki kysymykset:")
for col in numeric_columns:
    st.write(f"Kysymys {col.split('_')[0]}: {question_descriptions[col]}")