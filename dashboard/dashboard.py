import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import numpy as np
import datetime

# Database connection
engine = create_engine('postgresql://airflow:airflow@postgres:5432/airflow')

# Check if table exists
with engine.connect() as connection:
    check_table = text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'weather_data'
        );
    """)
    table_exists = connection.execute(check_table).scalar()
    
    if table_exists:
        # Get column names first
        columns_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'weather_data';
        """)
        columns = [row[0] for row in connection.execute(columns_query)]
        
        # Remove debug information
        df = pd.read_sql("SELECT * FROM weather_data", engine)
        
        if df.empty:
            st.warning("La table 'weather_data' est vide.")
        else:
            # Format data
            df["time"] = pd.to_datetime(df["time"])
            df["temperature"] = df["temperature"].round(2)
            df["windspeed"] = df["windspeed"].round(2)
        
            # TITRE
            st.title("📊 Dashboard météo")
        
            # Filtre de ville
            selected_city = st.selectbox("🏙️ Sélectionner une ville", df["city"].unique())
            df = df[df["city"] == selected_city]

            # Vérifier que le DataFrame n'est pas vide avant de continuer
            if not df.empty:
                # Obtenir l'heure actuelle
                current_time = datetime.datetime.now()

                # Calculer la différence absolue entre chaque heure du DataFrame et l'heure actuelle
                df['time_diff'] = abs(df['time'] - current_time)
                
                # Trouver l'index de l'entrée la plus proche de l'heure actuelle
                closest_time_idx = df['time_diff'].idxmin()
                
                # KPI - 3 colonnes
                col1, col2, col3 = st.columns(3)
                col1.metric("🌡️ Température", f"{df.loc[closest_time_idx, 'temperature']} °C")
                col2.metric("💨 Vent", f"{df.loc[closest_time_idx, 'windspeed']} m/s")
                col3.metric("📅 Date", df.loc[closest_time_idx, 'time'].strftime("%d/%m/%Y"))
                
                # Tableau horizontal des températures
                st.subheader("🕒 Températures horaires")
                today = pd.Timestamp.now().date()
                daily_temps = df[df['time'].dt.date == today].copy()
                
                if not daily_temps.empty:
                    # Création d'un DataFrame horizontal
                    hourly_data = daily_temps.set_index('time')['temperature'].round(0).astype(int)
                hourly_data.index = hourly_data.index.strftime('%H:%M')
                hourly_df = pd.DataFrame([hourly_data.values], columns=hourly_data.index)
                
                # Style pour le défilement horizontal
                st.markdown("""
                    <style>
                        .horizontal-scroll {
                            overflow-x: auto;
                            white-space: nowrap;
                        }
                    </style>
                """, unsafe_allow_html=True)
                
                # Affichage du tableau
                st.dataframe(
                    hourly_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={col: st.column_config.NumberColumn(col, format="%d °C") for col in hourly_df.columns}
                )

            # Températures sur une semaine
            st.subheader("📅 Prévisions sur 7 jours")
            today = pd.Timestamp.now().date()
            end_date = today + pd.Timedelta(days=6)  # 7 jours à venir
            
            # Créer une plage de dates future
            date_range = pd.date_range(start=today, end=end_date)
            weekly_temps = df[df['time'].dt.date.isin(date_range.date)]
            
            if not weekly_temps.empty:
                # Création du tableau
                weekly_stats = weekly_temps.groupby(pd.Grouper(key='time', freq='D')).agg(
                    Max=('temperature', 'max'),
                    Min=('temperature', 'min')
                ).reindex(date_range)  # Forcer 7 entrées
                
                # Remplir les dates manquantes
                weekly_stats = weekly_stats.reset_index().rename(columns={'index': 'time'})
                weekly_stats['Date'] = weekly_stats['time'].dt.strftime('%d/%m')
                weekly_stats['Max'] = weekly_stats['Max'].fillna(0).round(0).astype(int)
                weekly_stats['Min'] = weekly_stats['Min'].fillna(0).round(0).astype(int)
                
                # Affichage du tableau
                st.dataframe(
                    weekly_stats[['Date', 'Max', 'Min']],
                    column_config={
                        "Date": st.column_config.TextColumn("📅 Date"),
                        "Max": st.column_config.NumberColumn("🌡️ Max (°C)", format="%d °C"),
                        "Min": st.column_config.NumberColumn("❄️ Min (°C)", format="%d °C")
                    },
                    hide_index=True,
                    use_container_width=True
                )

            # Filtre de date
            min_date = pd.to_datetime(df['time'].min()).to_pydatetime()
            max_date = pd.to_datetime(df['time'].max()).to_pydatetime()
            date_range = st.slider("🕐 Période :", 
                                min_value=min_date,
                                max_value=max_date,
                                value=(min_date, max_date),
                                format="DD/MM/YY")
            df_filtered = df[(df['time'] >= date_range[0]) & (df['time'] <= date_range[1])]

            # Filtre d'agrégation temporelle
            aggregation = st.selectbox("📅 Aggrégation temporelle", 
                                      ["Heure", "Jour", "Semaine", "Mois"],
                                      index=0)
            
            # Préparation des données agrégées
            numeric_cols = df_filtered.select_dtypes(include=[np.number]).columns
            if aggregation == "Heure":
                period_df = df_filtered.set_index('time')[numeric_cols].resample('H').mean()
            elif aggregation == "Jour":
                period_df = df_filtered.set_index('time')[numeric_cols].resample('D').mean()
            elif aggregation == "Semaine":
                period_df = df_filtered.set_index('time')[numeric_cols].resample('W').mean()
            else:  # Mois
                period_df = df_filtered.set_index('time')[numeric_cols].resample('M').mean()

            # [REMOVED] Tableau des données filtrées

            # Graphique températures
            st.subheader(f"🌡️ Températures ({aggregation.lower()})")
            st.line_chart(period_df[["temperature"]])
            
            # Graphique vent
            st.subheader(f"💨 Vitesse du vent ({aggregation.lower()})")
            st.line_chart(period_df[["windspeed"]])
            
            # Graphique précipitations
            st.subheader(f"🌧️ Précipitations ({aggregation.lower()})")
            if aggregation == "Heure":
                st.line_chart(period_df[["precipitation"]])
            else:
                # Somme des précipitations pour les agrégations > heure
                precip_df = df_filtered.set_index('time')['precipitation'].resample(period_df.index.inferred_freq[0]).sum().to_frame()
                st.line_chart(precip_df)

            # Graphique par ville
            if len(df_filtered["city"].unique()) > 1:
                st.subheader("🏙️ Températures par ville")
                city_temp = df_filtered.groupby("city")[["temperature_max", "temperature_min"]].mean()
                st.bar_chart(city_temp)

            # Graphique conditions météo
            if "weathercode" in df_filtered.columns:
                st.subheader("☁️ Répartition des conditions météo")
                st.bar_chart(df_filtered["weathercode"].value_counts())
            
            # [REMOVED] Tableau des températures sur 10 jours
    else:
        st.error("❌ La table 'weather_data' n'existe pas encore. Lance d'abord le DAG Airflow.")