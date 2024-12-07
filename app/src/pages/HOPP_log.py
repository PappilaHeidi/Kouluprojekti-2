import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as plt
import requests
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# Asetetaan API-osoite
api_url = "http://database:8081/get/silver/hopp"

@st.cache_data
def fetch_data():
    """Hakee datan REST-API:n kautta ja käsittelee sen."""
    response = requests.get(api_url)
    if response.status_code == 200:
        data = pd.DataFrame(response.json())
        
        # Löydä kaikki numerolla alkavat sarakkeet ja poista duplikaatit
        numeric_columns = list(dict.fromkeys([
            col for col in data.columns 
            if col.split('_')[0].isdigit()
        ]))
        
        # Suorita vastaavat käsittelyt kuin alkuperäisessä koodissa
        selected_units = ["AIKTEHOHO", "EALAPSAIK", "ENSIHOITO"]
        data = data[data["unit_code"].isin(selected_units)]
        
        # Korvaa 'E' arvot NaN:lla ja muunna numerot
        data[numeric_columns] = data[numeric_columns].replace('E', pd.NA)
        data[numeric_columns] = data[numeric_columns].apply(pd.to_numeric, errors='coerce')
        
        # Näytä quarter-sarakkeen sisältö debuggausta varten
        st.write("Unique quarters:", data['quarter'].unique())
        
        # Muunna quarter aikasarjamuotoon turvallisemmin
        def quarter_to_date(q):
            try:
                quarter, year = q.split('_')
                month = (int(quarter) - 1) * 3 + 1  # Q1->1, Q2->4, Q3->7, Q4->10
                # Varmista että vuosiluku on oikein muodostettu
                if len(year) == 2:
                    year = '20' + year
                return f"{year}-{month:02d}-01"
            except Exception as e:
                st.error(f"Virhe päivämäärän muodostamisessa arvolle {q}: {str(e)}")
                return None
            
        # Muunna päivämäärät ja tarkista virheet
        dates = data['quarter'].apply(quarter_to_date)
        if dates.isna().any():
            st.error("Joitakin päivämääriä ei voitu muuntaa!")
            st.write("Virheelliset rivit:", data[dates.isna()]['quarter'])
            
        data['quarter_date'] = pd.to_datetime(dates)
        data = data.sort_values('quarter_date')
        
        return data, numeric_columns, selected_units
    else:
        st.error(f"Virhe haettaessa dataa: {response.status_code}")
        response.raise_for_status()

def prepare_features(data, question, unit):
    """Valmistele aikasarjaominaisuudet ennustamista varten."""
    unit_data = data[data['unit_code'] == unit].copy()
    
    # Varmista että data on aikajärjestyksessä
    unit_data = unit_data.sort_values('quarter')
    
    # Luo perusfeaturet
    features = pd.DataFrame()
    features['value'] = unit_data[question]
    
    # Täytä puuttuvat arvot edellisellä arvolla
    features['value'] = features['value'].fillna(method='ffill')
    
    # Tallenna viimeisen 3 kvartaalin keskiarvo jos mahdollista
    features['current_avg'] = features['value'].rolling(window=3, min_periods=1).mean()
    
    # Luo lag-featuret, vaadi vain yksi edellinen arvo
    if len(features) >= 2:
        features['lag1'] = features['value'].shift(1)
    
    # Lisää trendi
    features['trend'] = range(len(features))
    
    # Normalisoi arvot 0-1 välille
    features['norm_value'] = (features['value'] - features['value'].min()) / \
                           (features['value'].max() - features['value'].min())
    
    # Poista NaN-rivit
    features = features.dropna()
    
    # Vaadi vähintään 2 datapistettä (aiemman 3 sijaan)
    return features if len(features) >= 2 else None

def sort_quarters(df):
    """Järjestää vuosineljännekset oikeaan järjestykseen."""
    def quarter_to_float(q):
        try:
            quarter, year = q.split('_')
            return float(year) + (float(quarter) - 1) / 4
        except:
            return 0

    if isinstance(df.index, pd.MultiIndex):
        quarter_level = 1
        sorted_quarters = sorted(df.index.levels[quarter_level], key=quarter_to_float)
        return df.reindex(level=quarter_level, labels=sorted_quarters)
    else:
        return df.sort_values(by='quarter', key=lambda x: x.map(quarter_to_float))
    
def quarter_to_float(q):
    """Muuntaa kvarttaalimerkkijonon numeroksi järjestämistä varten."""
    try:
        quarter, year = q.split('_')
        return float(year) + (float(quarter) - 1) / 4
    except:
        return 0

def create_bar_chart(data, numeric_columns, selected_question):
    """Luo interaktiivinen palkkidiagrammi järjestetyillä kvarttaaleilla."""
    # Järjestä data kvarttaalien mukaan
    data = data.copy()
    data['sort_key'] = data['quarter'].map(quarter_to_float)
    data = data.sort_values('sort_key')
    
    traces = []
    colors = {
        "AIKTEHOHO": "blue",
        "EALAPSAIK": "green", 
        "ENSIHOITO": "red"
    }
    
    # Laske kansallinen keskiarvo vain jos on vähintään 2 yksikköä dataa
    national_avg = (data.groupby('quarter')[selected_question]
                   .agg(['mean', 'count'])
                   .reset_index())
    
    # Varmista että kvarttaalit ovat oikeassa järjestyksessä
    national_avg['sort_key'] = national_avg['quarter'].map(quarter_to_float)
    national_avg = national_avg.sort_values('sort_key')
    
    # Näytä yksiköiden palkit
    for unit in ["AIKTEHOHO", "EALAPSAIK", "ENSIHOITO"]:
        unit_data = data[data['unit_code'] == unit]
        
        traces.append(
            plt.Bar(
                name=unit,
                x=unit_data['quarter'],
                y=unit_data[selected_question],
                marker_color=colors[unit],
                hovertemplate=(
                    f'{unit}<br>'
                    f'Arvo: %{{y:.2f}}<br>'
                    f'Kvartaali: %{{x}}<extra></extra>'
                )
            )
        )
    
    # Lisää kansallinen keskiarvo vain niille kvartaaleille, joissa on tarpeeksi dataa
    valid_quarters = national_avg[national_avg['count'] >= 2]
    
    traces.append(
        plt.Scatter(
            name='Kansallinen keskiarvo',
            x=valid_quarters['quarter'],
            y=valid_quarters['mean'],
            mode='lines+markers',
            line=dict(color='black', dash='dot', width=2),
            hovertemplate=(
                'Kansallinen keskiarvo<br>'
                'Arvo: %{y:.2f}<br>'
                'Yksiköitä datassa: %{text}<extra></extra>'
            ),
            text=valid_quarters['count']
        )
    )
    
    # Järjestä x-akselin kvarttaalit
    unique_quarters = sorted(data['quarter'].unique(), key=quarter_to_float)
    
    layout = plt.Layout(
        title={
            'text': f'{selected_question} - Yksikköjen kehitys',
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis=dict(
            title='Vuosineljännes',
            tickangle=45,
            type='category',
            categoryorder='array',
            categoryarray=unique_quarters
        ),
        yaxis=dict(
            title='Keskiarvo',
            range=[1, 5],
            dtick=1
        ),
        hovermode='closest',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        barmode='group'
    )
    
    fig = plt.Figure(data=traces, layout=layout)
    return fig

def train_prediction_model(features, threshold=4.5):
    """Kouluta ennustusmalli optimoiduilla parametreilla."""
    if features is None or len(features) < 2:
        return None, None
        
    # Määritä target (käytä kynnysarvoa 4.5)
    y = (features['value'] >= threshold).astype(int)
    
    # Tarkista onko tarpeeksi vaihtelua
    if len(y.unique()) < 2:
        return None, None
    
    # Käytä kaikkia featureita paitsi 'value' ja 'norm_value'
    feature_cols = [col for col in features.columns if col not in ['value', 'norm_value']]
    X = features[feature_cols]
    
    # Skaalaa featuret
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    try:
        # Kouluta malli optimoiduilla parametreilla
        model = LogisticRegression(
            random_state=42,
            max_iter=5000,
            C=0.8,
            class_weight='balanced',
            solver='liblinear',
            penalty='l1'
        )
        model.fit(X_scaled, y)
        return model, scaler
    except Exception as e:
        st.warning(f"Mallin koulutus epäonnistui: {str(e)}")
        return None, None

def predict_next_values(data, numeric_columns, selected_units, threshold=4.5):
    """Ennusta seuraavan kvartaalin arvot kaikille yksiköille ja kysymyksille."""
    predictions = {}
    
    for unit in selected_units:
        predictions[unit] = {}
        unit_data = data[data['unit_code'] == unit]
        
        # Vaadi vähintään 2 datapistettä
        if len(unit_data) < 2:
            continue
            
        for question in numeric_columns:
            try:
                # Valmistele featuret
                features = prepare_features(data, question, unit)
                if features is None:
                    continue
                    
                # Kouluta malli
                model, scaler = train_prediction_model(features, threshold)
                if model is None:
                    continue
                
                # Valmistele viimeisimmät featuret ennustusta varten
                latest_features = features.iloc[-1:].copy()
                latest_features['trend'] += 1
                
                # Säilytä kaikki samat sarakkeet kuin koulutusvaiheessa
                X_features = [col for col in features.columns if col not in ['value', 'norm_value']]
                X_pred = latest_features[X_features]
                
                # Tee ennuste
                X_pred_scaled = scaler.transform(X_pred)
                
                # Tallenna ennuste ja nykyarvo (1-3 kk keskiarvo)
                current_value = features['current_avg'].iloc[-1]
                pred_proba = model.predict_proba(X_pred_scaled)[0][1]
                
                # Laske käytettyjen kvarttaalien määrä keskiarvossa
                used_quarters = min(3, len(features))
                
                predictions[unit][question] = {
                    'current': current_value,
                    'pred_proba': pred_proba,
                    'trend': 'up' if pred_proba > 0.5 else 'down',
                    'quarters_used': used_quarters
                }
                
            except Exception as e:
                st.warning(f"Virhe käsiteltäessä kysymystä {question}: {str(e)}")
                continue
    
    return predictions

def display_predictions(predictions, data):
    """Näytä ennusteet käyttäjäystävällisessä muodossa."""
    st.header("Ennusteet seuraavalle kvartaalille")
    st.write(f"Todennäköisyys että arvo ylittää 4.5")
    
    for unit in predictions.keys():
        st.subheader(f"Yksikkö: {unit}")
        
        # Muunna yksikön ennusteet DataFrameksi
        pred_data = []
        for question, pred in predictions[unit].items():
            if pred is not None:
                trend_symbol = '↑' if pred['trend'] == 'up' else '↓'
                
                pred_data.append({
                    'Kysymys': question,
                    f'Nykyarvo ({pred["quarters_used"]}kk ka)': f"{pred['current']:.2f}",
                    'Ennuste': trend_symbol,
                    'Todennäköisyys ≥4.5': f"{pred['pred_proba']*100:.1f}%"
                })
        
        if pred_data:
            pred_df = pd.DataFrame(pred_data)
            
            # Luodaan style funktio joka palauttaa värin trendin mukaan
            def style_arrow(val):
                if val == '↑':
                    return 'color: green'
                elif val == '↓':
                    return 'color: red'
                return ''
            
            # Käytä style_arrow-funktiota vain Ennuste-sarakkeeseen
            styled_df = pred_df.style.applymap(
                style_arrow,
                subset=['Ennuste']
            )
            
            st.dataframe(styled_df, hide_index=True)
        else:
            st.write("Ei riittävästi dataa ennusteiden tekemiseen.")
            unit_data = data[data['unit_code'] == unit]
            st.write(f"Saatavilla oleva data yksikölle {unit}:")
            st.write(f"Rivejä: {len(unit_data)}")
            st.write("Kvarttaalit:", unit_data['quarter'].unique())

def main():
    st.title("HOPPlop Logistinen Regressio hässäkkä homma juttu")

    # Hakee ja käsittelee datan
    data, numeric_columns, selected_units = fetch_data()

    # Valitse kysymys
    selected_question = st.selectbox("Valitse kysymys", numeric_columns)

    # Luo kuvaaja
    fig = create_bar_chart(data, numeric_columns, selected_question)
    
    # Näytä kuvaaja ja selite
    st.plotly_chart(fig, use_container_width=True, key="main_chart")
    
    st.info("""
        **Huomio kansallisesta keskiarvosta:**
        - Keskiarvo lasketaan vain niille kvartaaleille, joissa on dataa vähintään kahdelta yksiköltä
        - Hover-tiedoissa näkyy, kuinka monen yksikön dataan keskiarvo perustuu
    """)
    
    # Tee ennusteet
    predictions = predict_next_values(data, numeric_columns, selected_units)
    
    # Näytä ennusteet
    display_predictions(predictions, data)

if __name__ == "__main__":
    main()