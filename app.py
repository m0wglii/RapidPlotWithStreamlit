# app.py

# Die folgenden Zeilen importieren verschiedene Module, die im Code verwendet werden.
import streamlit as st  # Streamlit ist ein Framework, um Web-Apps zu erstellen.
import pandas as pd  # Pandas ermöglicht die Datenverarbeitung.
import requests  # Mit requests kann ich Daten aus dem Internet abrufen.
import matplotlib.pyplot as plt  # Zum Erstellen von Diagrammen.
import folium  # Folium wird verwendet, um interaktive Karten zu erstellen und darzustellen.
from folium.plugins import HeatMap  # HeatMap ist ein Plugin von Folium, um Heatmaps auf Karten zu erzeugen.
import streamlit_folium  # Dieses Modul ermöglicht es, Folium-Karten in einer Streamlit-App anzuzeigen.

# Daten über die API abrufen
base_url = "https://data.police.uk/api"
endpoint = f"{base_url}/crimes-street/all-crime?lat=51.5074&lng=-0.1278&date=2022-01"
response = requests.get(endpoint)  # Sendet eine Anfrage an den Endpunkt.
data = response.json()  # Wandelt die Antwort in ein JSON-Format um.
df = pd.DataFrame(data)  # Wandelt das JSON in eine Dataframe (eine Tabelle) um.

# Titel der Web-App festlegen.
st.title('Analyse von Polizeidaten aus London mit Streamlit')

# Schalter um die Rohdaten in der App anzuzeigen
if st.checkbox('Zeige Datengrundlage'):
    st.write(df)  # Zeigt die Tabelle in der Web-App an.

# 1. Balkendiagramm Verbrechenskategorien:
st.subheader("Verbrechen nach Kategorien")
crime_category_count = df['category'].value_counts()  # Zählt, wie oft jede Kategorie vorkommt.
st.bar_chart(crime_category_count)  # Zeigt das Balkendiagramm in der Web-App an.

# 2. Tortendiagramm zum Ergebnisstatus:
st.subheader("Verteilung der Ermittlungsergebnisse")
# Aus der Tabelle werden alle Zeilen entfernt, in denen 'outcome_status' fehlt.
# Anschließend wird für jede verbleibende Zeile der Wert 'category' innerhalb von 'outcome_status' extrahiert.
outcome_status = df.dropna(subset=['outcome_status']).apply(lambda x: x['outcome_status']['category'], axis=1)
# Zählt, wie oft jeder 'outcome_status' vorkommt und speichert die Ergebnisse.
outcome_count = outcome_status.value_counts()

# Kleinere Segmente in einer "Sonstiges"-Kategorie zusammenfassen
threshold = 0.02 * outcome_count.sum()  # Schwellenwert definieren.
mask = outcome_count > threshold  # Bestimmt, welche Werte über dem Schwellenwert liegen.

# Kleinere Segmente von denen über dem Schwellenwert trennen
small_slices = outcome_count[~mask]
larger_slices = outcome_count[mask]

# Bei Vorhandensein kleinerer Segmente, 'Sonstiges' Kategorie dafür erstellen
if len(small_slices) > 0:
    larger_slices['Other'] = small_slices.sum()

outcome_count = larger_slices

fig, ax = plt.subplots()
wedges, texts, autotexts = ax.pie(outcome_count, autopct='%d%%', startangle=90, pctdistance=0.5,
                                  textprops=dict(color="k", fontsize=3))

# Weil Tortendiagramme grundsätzlich unbeliebt sind, mache ich ein Donut-Diagramm daraus ;)
centre_circle = plt.Circle((0, 0), 0.70, fc='white')  # Zeichnet einen weißen Kreis in der Mitte
fig.gca().add_artist(centre_circle)

# Legende hinzufügen
ax.legend(wedges, outcome_count.index, title="Kategorien", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

ax.set_title("Verteilung der Ermittlungsergebnisse")
ax.axis('equal')

plt.tight_layout()
st.pyplot(fig)

# Breiten- und Längengrade aus der Spalte 'location' extrahieren.
locations_df = pd.json_normalize(df['location'])
locations = locations_df[['latitude', 'longitude']].copy()
locations['latitude'] = locations['latitude'].astype(float)
locations['longitude'] = locations['longitude'].astype(float)

# 3. Heatmap für Verbrechensstandorte
st.subheader("Heatmap Verbrechensstandorte")

# Erstellen einer Karte
m = folium.Map(location=[51.5074, -0.1278], zoom_start=13)

# Daten für die Heatmap hinzufügen
heat_data = [[row['latitude'], row['longitude']] for index, row in locations.iterrows()]
HeatMap(heat_data).add_to(m)

# Die Karte in Streamlit anzeigen
streamlit_folium.folium_static(m)
