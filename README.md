# 🌤️ Weather Data Pipeline (ETL + Dashboard)

Un projet complet de pipeline de données météo, orchestré avec Airflow, conteneurisé avec Docker, et visualisé avec Streamlit.

## 🚀 Objectif

Mettre en place un pipeline **ETL** de bout en bout :
- 🔄 Extraction des données depuis l'API Open-Meteo
- ⚙️ Transformation et nettoyage avec Python
- 🗃️ Chargement dans une base PostgreSQL
- 📊 Visualisation via un dashboard interactif Streamlit

## 🛠️ Technologies utilisées

- Python 3.10
- Apache Airflow
- PostgreSQL
- Docker & Docker Compose
- Streamlit
- SQLAlchemy / Pandas

## 📁 Architecture du projet

weather-data-pipeline/ ├── dags/ # DAG Airflow ├── dashboard/ # App Streamlit ├── docker-compose.yml ├── Dockerfile ├── requirements.txt └── README.md


## 🐳 Lancer le projet avec Docker

```bash
# Construire et démarrer tous les services
docker-compose up --build 
```
## 🚀 Accéder à l'application

- 🔗 Airflow : http://localhost:8080
- 🔗 Dashboard Streamlit : http://localhost:8501

---

## 📊 Résultat

- ✅ Données météo mises à jour automatiquement via **Airflow**
- ✅ Stockées dans **PostgreSQL**
- ✅ Affichées dans un **dashboard interactif** avec Streamlit

---

## 🙋‍♂️ Auteur

**Aboubacrine Seck**  
👨‍💻 Étudiant en Master Data & IA @ HETIC  
📧 [aboubacrineseckpro@gmail.com](mailto:aboubacrineseckpro@gmail.com)
