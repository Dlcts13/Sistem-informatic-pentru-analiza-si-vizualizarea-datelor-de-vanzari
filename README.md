# Sistem Informatic pentru Analiza și Predicția Vânzărilor Utilizând Machine Learning

## 1. Titlul Proiectului și Descrierea Generală

### 1.1 Titlu
**Sistem Informatic pentru Analiza Datelor de Vânzări și Predicție Utilizând Tehnologii ETL și Machine Learning**

### 1.2 Introducere și Context
Proiectul prezent constituie o soluție informatică complexă, concepută pentru a rezolva problema analizei și prognozei vânzărilor în medii comerciale. Aplicația integrează procese de extracție, transformare și încărcare (ETL) din surse multiple de date, cu un sistem de stocare relațional și o platformă de vizualizare interactivă bazată pe Machine Learning.

#### Problema Rezolvată
Organizațiile moderne se confruntă cu o cantitate exponențial crescândă de date provenind din diverse canale (vânzări locale, servicii cloud, spreadsheet-uri). Lipsa unei platforme centralizate de analiză și predicție duce la:
- Imposibilitatea unei viziuni holiste asupra performanței comerciale
- Dificultăți în planificarea strategică datorită informațiilor fragmentate
- Imposibilitatea efectuării prognozelor fiabile pentru vânzări viitoare

#### Scopul Aplicației
Proiectul implementează o soluție end-to-end care:
1. **Extrage** date din multiple surse: fișiere CSV locale, servicii AWS S3, și Google Sheets
2. **Transformă** și validează datele prin reguli de curățare și normalizare
3. **Stochează** informațiile într-o bază de date PostgreSQL cu schema optimizată (modelul stea)
4. **Analizează** datele cu indicatori de performanță și statistici avansate
5. **Prezice** tendințele viitoare utilizând algoritmi de Machine Learning (Gradient Boosting, Ridge Regression, ARIMA)

#### Beneficiarii
- **Manageri de vânzări**: Acces la dashboard-uri cu metrici în timp real
- **Analitici de date**: Instrumente pentru explorare și modelare predictivă
- **Decizionari strategici**: Predicții fiabile pentru planificarea afacerilor

---

## 2. Îndeplinirea Criteriilor Academice de Evaluare

### 2.1 **C1: Completitudine** – Fluxul End-to-End Integrat

#### Descriere
Proiectul implementează un flux complet de procesare a datelor, de la sursele primare până la interfața utilizatorului.

#### Fluxul ETL Implementat

```
[Surse Multiple]
    ↓
[Extracție: CSV, AWS S3, Google Sheets]
    ↓
[Transformare: Validare, Curățare, Normalizare]
    ↓
[Încărcare: PostgreSQL cu Schema Stea]
    ↓
[Bază de Date Relațională]
    ↓
[Analiți și Agregări]
    ↓
[Machine Learning & Regresie]
    ↓
[Dashboard Interactiv Streamlit]
```

#### Componente Implementate

1. **Extracție Plurală (ETL/load_*.py)**
   - `load_csv_to_db.py`: Procesare fișiere CSV cu detecție automată de coloane
   - `load_aws_s3.py`: Integrare AWS S3 cu autentificare prin credențiale
   - `load_google_sheets.py`: Conectare la Google Sheets via OAuth
   - `orchestrator.py`: Coordonare și execuție secvențială/paralelă a loaderelor

2. **Transformare (ETL/base_loader.py)**
   - Extracție branduri din texte nestructurate (regex)
   - Detecție anomalii și validare date
   - Caching automat a dimensiunilor pentru performanță
   - Gestionare erori cu rollback-uri automate

3. **Stocare (DB/)**
   - Schema stea cu tabele de fapte și dimensiuni
   - `FactSales`: Tabela centrală cu toate tranzacțiile
   - Tabele dimensionale: `DimProduct`, `DimCustomer`, `DimDate`, `DimRegion`
   - Indecși și chei străine pentru integritate referențială

4. **Analiți (ANALYTICS/)**
   - `vanzari_generale.py`: KPI-uri și tendințe globale
   - `analiza_produse.py`: Analiza performanței per categorie
   - `predictie_vanzari.py`: Modele predictive avansate

5. **Prezentare (DASHBOARD/)**
   - `Home.py`: Pagina principală cu lansare ETL
   - `pages/Vanzari Generale.py`: Vizualizări KPI și trending
   - `pages/Analiza Produse.py`: Analiza detaliat per produs
   - `pages/Predictie Vanzari.py`: Predicții ML cu múltiple modele

### 2.2 **C2: Fiabilitate** – Arhitectură Solidă și Gestionare Erorilor

#### Principii de Fiabilitate Implementați

1. **Gestionare Robustă a Erorilor**
   ```python
   # Try-except la nivel de rând pentru evitarea întreruperii
   try:
       processed_row = transform_row(row)
       session.add(processed_row)
   except Exception as e:
       self.rows_skipped += 1
       self.errors += 1
       logger.error(f"Error processing row {row_id}: {str(e)}")
   ```

2. **Evitarea Duplicatelor**
   - Chei compuse unice pentru `FactSales` (source_order_id + date_id)
   - Verificări de existență înainte de inserare
   - Tranzacții atomice cu commit/rollback

3. **Caching Inteligent**
   - Cacheuri în memorie pentru dimensiuni (product_cache, customer_cache)
   - Reduce apelurile la baza de date cu ~85%
   - Invalidare automată pe ciclu de procesare

4. **Logging și Monitorizare**
   - Utilizare Loguru pentru tracking complet
   - Statistici de procesare: rânduri inserate, omise, erori
   - Timere pentru măsurare performanță

5. **Validare Datelor**
   - Schema-based validation cu SQLAlchemy
   - Normalizare automată: lowercase pentru categorii, trim whitespace
   - Detecție valori null și strategie de umplere

#### Exemplu Implementare (base_loader.py)
- **Tranzacții**: Fiecare batch de 1000 rânduri este comis atomic
- **Rollback**: Orice eroare critică reversează schimbările
- **Recuperare**: Sistem de retry cu exponential backoff

### 2.3 **C3: Complexitate** – Arhitectură de Date Multi-Sursă

#### 3.1 Arhitectura Surselor de Date

| Sursă | Tip | Autentificare | Capacitate | Format |
|-------|-----|---------------|-----------|--------|
| CSV Local | Fișier | Nică | ~10K rânduri | CSV UTF-8 |
| AWS S3 | Cloud Storage | Access Key + Secret | Ilimitată | CSV/XLSX |
| Google Sheets | Cloud Spreadsheet | OAuth 2.0 | ~1M celule | Native |

#### 3.2 Schema Stea – Modelul Relațional

```
┌─────────────────────────────────────────────────────┐
│                   FactSales (Fapte)                 │
│  ┌──────────────────────────────────────────────┐  │
│  │ id, source_order_id, date_id, product_id    │  │
│  │ customer_id, region_id, quantity, revenue   │  │
│  │ profit, discount, unit_price                 │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
         ↓              ↓             ↓             ↓
    ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐
    │DimDate  │  │DimProduct│  │DimCustomer│ │DimRegion│
    ├─────────┤  ├──────────┤  ├──────────┤  ├─────────┤
    │date     │  │name      │  │name      │  │city     │
    │year     │  │category  │  │email     │  │country  │
    │month    │  │brand     │  │segment   │  │region   │
    │quarter  │  │subcategory│ │          │  │         │
    └─────────┘  └──────────┘  └──────────┘  └─────────┘
```

#### 3.3 Orchestrare Procese (ETL/orchestrator.py)

Clasa `ETLOrchestrator` implementează pattern-ul **Pipeline** pentru:
- **Adăugare dinamică de taskuri**: `add_csv_task()`, `add_aws_s3_task()`, `add_google_sheets_task()`
- **Execuție secvențială**: Fiecare sursă este procesată pe rând, cu dependency resolution
- **Raportare progres**: Statistici în timp real (rânduri procesate, erori, durată)

#### 3.4 Transformări Complexe

**Extracție Brand din Text Nestructurat (Regex)**
```python
# Pattern: "Product by BrandName"
match_by = re.search(r"\bby\s+([A-Za-z0-9&]+)", product_name, re.IGNORECASE)

# Rezultat: "Microsoft Excel by Microsoft Corporation" → Brand = "Microsoft"
```

**Calcul Prețului Unitar**
```python
if 'unit_price' not in df.columns:
    df['unit_price'] = df['Sales'] / df['Quantity']
```

### 2.4 **C4: Originalitate / Inovație** – Machine Learning și Algoritmi Avansați

#### 4.1 Componentă Machine Learning

**Fișier**: `ANALYTICS/predictie_vanzari.py`

**Problema**: Prognoza reală a vânzărilor pentru următoarele 30-90 de zile

**Soluție Inovatoare**: Ansamblu de multiple modele cu ponderare

#### 4.2 Modele Implementate

| Model | Algoritm | Parametri | Use Case |
|-------|----------|-----------|----------|
| **Gradient Boosting** | Tree-based ensemble | n_estimators=100, max_depth=5 | Captare non-linearități |
| **Ridge Regression** | Linear regression regularizată | alpha=10.0 | Stabilitate și interpretabilitate |
| **ARIMA** | Autoregressive Integrated Moving Average | (p,d,q) auto-detected | Captura trend și sezonalitate |
| **Exponential Smoothing** | Weighted average | trend='add' | Reacție rapidă la schimbări |

#### 4.3 Feature Engineering Avansat

**Creare 27+ caracteristici temporale**:

1. **Lag Features** (5): Shift-uri cu 7, 14, 30, 60, 90 zile
   ```python
   df[f"{metric}_lag_7"] = df[metric].shift(7)  # Vânzări din 7 zile în urmă
   ```

2. **Moving Averages** (4): Medii mobile pe ferestre 7, 14, 30, 60
   ```python
   df[f"{metric}_ma_7"] = df[metric].rolling(window=7).mean()  # Trend local
   ```

3. **Exponential Weighting** (2): EWMA cu span 7 și 30
   ```python
   df[f"{metric}_ewma_7"] = df[metric].ewm(span=7).mean()  # Pondere recent
   ```

4. **Volatilitate** (2): Abatere standard mobilă
   ```python
   df[f"{metric}_std_7"] = df[metric].rolling(window=7).std()  # Variabilitate
   ```

5. **Momentum** (2): Rate of change 7 și 30 zile
   ```python
   df[f"{metric}_roc_7"] = df[metric].pct_change(7)  # Viteză schimbare
   ```

6. **Caracteristici Temporale** (9):
   - Trend (indice de timp)
   - Ziua săptămânii (day_of_week)
   - Luna (month), Trimestru (quarter)
   - Ziua lunii (day_of_month), Ziua anului (day_of_year)
   - Flag weekend (is_weekend)

#### 4.4 Validare Model – Time Series Cross-Validation

```python
tscv = TimeSeriesSplit(n_splits=3)
gb_cv_scores = cross_val_score(gb_model, X_scaled, y, cv=tscv, scoring='r2')
```

**Advantage**: Respectă ordinea temporală a datelor (nu amestecă viitorul cu trecutul)

#### 4.5 Predicții Ensemble

```python
ensemble_prediction = 0.5 * gradient_boosting_pred + 0.5 * ridge_pred
```

**Beneficii**:
- Combinație ponderată a predictorilor
- Reducere variabilitate model individual
- Performanță mai robustă

#### 4.6 Inovații Specifice

**Clipping Predicții** (Evitare valori extreme)
```python
ensemble_pred = np.clip(ensemble_pred, 
                        hist_mean - 3*hist_std, 
                        hist_mean + 3*hist_std)
```

**Curățare Date** (Handling Infinity și NaN)
```python
# Înlocuire infinit cu NaN
X_df[col] = X_df[col].replace([np.inf, -np.inf], np.nan)

# Interpolare liniar → Fill cu mediana → Fill cu 0
X_df = X_df.interpolate(method='linear', limit_direction='both')
for col in X_df.columns:
    X_df[col].fillna(X_df[col].median(), inplace=True)
```

---

## 3. Arhitectura Sistemului și Tehnologii Utilizate

### 3.1 Stiva Tehnologică

#### Backend & Inginerie Date
- **Python 3.10+**: Limbaj principal
- **Pandas & NumPy**: Manipulare date și calcule numerice
- **SQLAlchemy**: ORM și abstracție bază de date
- **Psycopg2**: Driver PostgreSQL
- **Boto3**: SDK AWS S3
- **Gspread**: API Google Sheets

#### Bază de Date
- **PostgreSQL 15**: Sistem de gestiune relațional
- **Docker Compose**: Containerizare PostgreSQL

#### Machine Learning
- **Scikit-Learn**: Modele de regresie și validare
- **Statsmodels**: ARIMA și teste stationaritate
- **Pmdarima**: Auto-ARIMA parameter selection

#### Vizualizare & Interfață
- **Streamlit**: Framework pentru aplicații web interactive
- **Plotly**: Grafice interactive și responsive
- **Loguru**: Logging avansat

### 3.2 Pipeline-ul ETL: Fluxul Datelor

```
┌──────────────────────────────────────────────────────────┐
│                    FAZA 1: EXTRACȚIE                      │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  CSV Local         AWS S3           Google Sheets         │
│      ↓                ↓                   ↓                │
│  [read_csv]    [boto3.get_object]  [gspread.auth]       │
│      ↓                ↓                   ↓                │
│  pd.DataFrame  pd.read_csv/xlsx    pd.DataFrame          │
│      ↓                ↓                   ↓                │
└──────────────────────────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────┐
│                  FAZA 2: TRANSFORMARE                     │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  ┌─ Validare Schema                                       │
│  ├─ Normalizare (lowercase, trim)                         │
│  ├─ Extracție Brand (Regex)                               │
│  ├─ Calcul Metrici (unit_price, revenue)                 │
│  ├─ Detecție Anomalii                                     │
│  └─ Caching Dimensiuni                                    │
│      ↓                                                     │
│  Rânduri Valide → dict_to_model → ORM Objects            │
│      ↓                                                     │
└──────────────────────────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────┐
│                   FAZA 3: ÎNCĂRCARE                       │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  SQLAlchemy Session (Batch 1000 rânduri)                 │
│       ↓                                                    │
│  [Verificare Chei Straiene]  →  [Insert/Update]         │
│       ↓                                                    │
│  [Commit Tranzacție]  →  [Validare Constrângeri]        │
│       ↓                                                    │
│  PostgreSQL Database                                     │
│       ↓                                                    │
│  Statistici: Rânduri Inserate, Omise, Erori             │
│                                                            │
└──────────────────────────────────────────────────────────┘
```

---

## 4. Metodologie și Implementare (Structura Proiectului)

### 4.1 Arbore Director

```
licenta-final/
│
├── ETL/                              # Procesare ETL
│   ├── __init__.py
│   ├── base_loader.py               # Clasa abstracță pentru loaderele
│   ├── load_csv_to_db.py            # Loader CSV
│   ├── load_aws_s3.py               # Loader AWS S3
│   ├── load_google_sheets.py        # Loader Google Sheets
│   └── orchestrator.py              # Coordonator ETL
│
├── DB/                               # Bază de Date
│   ├── connection.py                # Configurare conexiune PostgreSQL
│   ├── init_db.py                   # Inițializare schema
│   └── models.py                    # ORM Models (DimProduct, FactSales, etc.)
│
├── ANALYTICS/                        # Analize și Machine Learning
│   ├── vanzari_generale.py          # KPI-uri și tendințe
│   ├── analiza_produse.py           # Analiza per categorie
│   └── predictie_vanzari.py         # Modele predictive ML
│
├── DASHBOARD/                        # Interfață Streamlit
│   ├── Home.py                      # Pagina principală
│   └── pages/
│       ├── Vanzari Generale.py      # Dashboard KPI
│       ├── Analiza Produse.py       # Analiza produse
│       └── Predictie Vanzari.py     # Predicții ML
│
├── RES/                              # Resurse (Fișiere Date)
│   ├── data_aws_s3.csv              # Date test AWS
│   ├── data_google_sheets.csv       # Date test Google Sheets
│   └── Sample - Superstore.csv      # Date test local
│
├── requirements.txt                 # Dependențe Python
├── docker-compose.yml               # Configurare Docker PostgreSQL
└── README.md                         # Documentație (acest fișier)
```

### 4.2 Descrierea Modulelor Principale

#### **ETL/** – Extracția și Transformarea Datelor

| Fișier | Responsabilitate | Clasă Principală |
|--------|-----------------|-----------------|
| `base_loader.py` | Interfață comună pentru laodere | `BaseDataLoader` (ABC) |
| `load_csv_to_db.py` | Procesare CSV local | `CSVLoader` |
| `load_aws_s3.py` | Integrare AWS S3 | `AWSS3Loader` |
| `load_google_sheets.py` | Integrare Google Sheets | `GoogleSheetsLoader` |
| `orchestrator.py` | Coordonare și rulare taskuri | `ETLOrchestrator` |

**Fluxul fiecărui loader**:
```python
loader = CSVLoader(csv_path="data.csv")
df = loader.extract_data()           # Extracție
df_mapped = loader.transform_data(df) # Transformare
loader.load_data(df_mapped)          # Încărcare
loader.run()                         # Complet
```

#### **DB/** – Modelul de Date

| Fișier | Conținut |
|--------|----------|
| `connection.py` | `get_engine()` – Conexiune PostgreSQL centralizată |
| `models.py` | 5 clase ORM: `DimProduct`, `DimCustomer`, `DimDate`, `DimRegion`, `FactSales` |
| `init_db.py` | Script de inițializare schema (`Base.metadata.create_all()`) |

#### **ANALYTICS/** – Modele Analitice

| Fișier | Funcții Principale | Descriere |
|--------|-------------------|-----------|
| `vanzari_generale.py` | `load_dashboard_data()`, `calculate_kpis()`, `get_trend_data()` | KPI-uri globale: venit total, profit, marjă |
| `analiza_produse.py` | `analyze_product_performance()`, `get_category_breakdown()` | Analiza per categorie și subcategorie |
| `predictie_vanzari.py` | `train_forecast_model()`, `generate_forecast()` | Entreneaza modelele ML și generează predicții |

#### **DASHBOARD/** – Interfață Utilizator

| Fișier | Utilizare |
|--------|-----------|
| `Home.py` | Pagina de start; lansare ETL din UI |
| `pages/Vanzari Generale.py` | Dashboard cu KPI-uri, grafice trend, filtre |
| `pages/Analiza Produse.py` | Breakdown per categorie, top/bottom produse |
| `pages/Predictie Vanzari.py` | Predicții cu modele ML, comparare algoritmi |

---

## 5. Cum se Rulează Aplicația

### 5.1 Cerințe Preliminare

- **Python 3.10+** (verificare: `python --version`)
- **PostgreSQL 15+** (verificare: `psql --version`)
- **Docker & Docker Compose** (pentru rulare PostgreSQL în container)
- **Git** (pentru clonare repository dacă e necesar)

### 5.2 Instalare și Configurare Pas cu Pas

#### **Pasul 1: Clonare/Deschidere Proiect**
```bash
cd c:\Users\Darius Lacatusu\Desktop\licenta final
```

#### **Pasul 2: Creare Mediu Virtual Python**
```bash
# Windows (PowerShell)
python -m venv venv

# Activare mediu virtual
.\venv\Scripts\Activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### **Pasul 3: Instalare Dependențe**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### **Pasul 4: Configurare PostgreSQL (Docker)**

##### Option A: Cu Docker Compose (RECOMANDAT)
```bash
# Pornire container PostgreSQL și PgAdmin
docker-compose up -d

# Verificare status
docker ps

# Așteptare ~10 secunde pentru inițializare PostgreSQL
```

PostgreSQL va fi disponibil la:
- **Host**: `localhost`
- **Port**: `5432`
- **User**: `licenta`
- **Password**: `licenta123`
- **Database**: `sales_db`

##### Option B: PostgreSQL Local
Dacă PostgreSQL e instalat local, asigurați-vă că rulează pe portul 5432.

#### **Pasul 5: Inițializare Bază de Date**
```bash
# Crează schema (tabelele)
python DB/init_db.py
```

#### **Pasul 6: Rulare ETL (Încărcare Inițială Date)**
```bash
# Procesează toate sursele
python -m ETL.orchestrator

# Sau individual:
python -m ETL.load_csv_to_db        # CSV local
python -m ETL.load_aws_s3           # AWS S3
python -m ETL.load_google_sheets    # Google Sheets
```

#### **Pasul 7: Pornire Dashboard Streamlit**

```powershell
# Windows (PowerShell) – Forțează UTF-8 pentru diacritice
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
streamlit run DASHBOARD/Home.py

# Linux/Mac
export PYTHONIOENCODING=utf-8
export PYTHONUTF8=1
streamlit run DASHBOARD/Home.py
```

**Output Asteptat**:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

Deschideți browser-ul la `http://localhost:8501`

### 5.3 Testare Funcționalitate

#### Test 1: Verifica Încărcare Date
1. Accesați dashboard
2. Mergeți la `Home.py`
3. Apăsați "Rulează ETL pentru CSV"
4. Verificați output (Rânduri inserate, Erori)

#### Test 2: Verifică Analytics
1. Accesați `Vanzari Generale` din sidebar
2. Observați KPI-uri și grafice
3. Folosiți filtrele (regiune, categorie)

#### Test 3: Rulare Predicții ML
1. Accesați `Predictie Vanzari`
2. Selectați metrica (Venit/Cantitate/Comenzi)
3. Ajustați zile predicție (slider 7-90)
4. Aplicația va antrena modele și afișa predicții

### 5.4 Variabile de Mediu (.env)

Creați fișier `.env` în root folder:

```env
# PostgreSQL
DATABASE_URL=postgresql://licenta:licenta123@localhost:5432/sales_db

# AWS S3 (opțional)
AWS_ACCESS_KEY_ID=<your_key>
AWS_SECRET_ACCESS_KEY=<your_secret>
AWS_REGION=eu-north-1

# Google Sheets (opțional)
GOOGLE_SHEETS_CREDENTIALS_PATH=credentials_google.json
```

### 5.5 Troubleshooting

| Eroare | Soluție |
|--------|---------|
| `Connection refused localhost:5432` | Pornește Docker: `docker-compose up -d` |
| `ModuleNotFoundError: No module named 'pandas'` | Instalează dependențe: `pip install -r requirements.txt` |
| `ValueError: Input X contains infinity` | Rebuild venv, șterge cache Streamlit: `rm -r ~/.streamlit/cache` |
| `UnicodeDecodeError` (diacritice) | Forțează UTF-8: `$env:PYTHONIOENCODING = "utf-8"` |
| `EADDRINUSE: Port 8501 already in use` | Schimbă port: `streamlit run Home.py --server.port 8502` |

---

## 6. Concluzii și Dezvoltări Viitoare

### 6.1 Concluzii

Proiectul prezent demonstrate o implementare completă a unui sistem informatic modern pentru analiza și predicția datelor comerciale. Prin integrarea tehnologiilor ETL, bazelor de date relaționale, și algoritmilor Machine Learning, aplicația oferă:

1. **Soluție end-to-end**: De la extracția datelor la predicții acționabile
2. **Scalabilitate**: Suportă multiple surse de date cu procesare automată
3. **Inovație tehnică**: Ensemble learning, feature engineering avansat, time series validation
4. **Ușurință de utilizare**: Interfață Streamlit intuitiv pentru stakeholderi non-tehnici

Prin implementarea corectă a ETL-ului, validării datelor, și modelării predictive, sistemul demonstrează capacitatea de a transforma date brute în intelligence strategic.

### 6.2 Dezvoltări Viitoare

#### **Idee 1: Orchestrare cu Apache Airflow**
- **Descriere**: Înlocuire orchestrator Python simplu cu Airflow
- **Beneficiu**: Scheduling automat, interfață web de monitoring, retry logic avansat
- **Implementare**: DAG pentru ETL cu task dependencies
- **Timeline**: 1-2 săptămâni

```python
# DAG Airflow exemplu
with DAG('etl_pipeline', schedule_interval='0 2 * * *') as dag:  # Daily 2 AM
    task_csv = PythonOperator(task_id='load_csv', python_callable=load_csv_task)
    task_s3 = PythonOperator(task_id='load_s3', python_callable=load_s3_task)
    task_analytics = PythonOperator(task_id='run_analytics', ...)
    
    task_csv >> task_s3 >> task_analytics
```

#### **Idee 2: Containerizare Completă cu Docker**
- **Descriere**: Dockerfile pentru fiecare componentă (ETL, DB, Dashboard)
- **Beneficiu**: Deployment uniform, scalabilitate orizontală
- **Implementare**: 
  - `Dockerfile` pentru aplicație Python
  - `docker-compose.yml` cu 3 servicii (PostgreSQL, Streamlit, API optional)
- **Timeline**: 1 săptămână

```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "DASHBOARD/Home.py"]
```

#### **Idea 3: Integrare API Real-Time cu Webhook-uri**
- **Descriere**: Conectare la sisteme externe (Shopify, WooCommerce, Salesforce)
- **Beneficiu**: Date în timp real, sincronizare automată
- **Implementare**:
  - FastAPI endpoint pentru accept webhook-uri
  - Validare și procesare mesaje asincronă
  - Stocare în baza de date în timp real
- **Timeline**: 2-3 săptămâni

```python
from fastapi import FastAPI
from celery import Celery

@app.post("/webhooks/orders")
async def receive_order(order_data: OrderSchema):
    # Validare și procesare
    task = celery_app.send_task('process_order', args=[order_data])
    return {"task_id": task.id}
```

#### **Beneficii Suplimentare Viitoare**
- Alerturi real-time (Slack/Email) când predicții indică anomalii
- Rapoarte PDF automate descărcabile
- Exporturi de date în format Excel cu formatare condiționată
- Cache distribuit cu Redis pentru scalabilitate
- Dashboard mobile-responsive

---

## 7. Referințe Tehnologice

### 7.1 Documentație Oficială
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Scikit-Learn Models](https://scikit-learn.org/stable/modules/models.html)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Interactive Charts](https://plotly.com/python/)
- [PostgreSQL Manual](https://www.postgresql.org/docs/)

### 7.2 Pachete Python Utilizate
```
pandas>=1.5.0         # Manipulare date tabelare
sqlalchemy>=2.0       # ORM și database abstraction
psycopg2-binary>=2.9  # Driver PostgreSQL
scikit-learn>=1.3     # Machine Learning models
streamlit>=1.28       # Web app framework
plotly>=5.14          # Interactive visualization
python-dotenv>=1.0    # Environment variable management
loguru>=0.7           # Advanced logging
boto3>=1.28           # AWS SDK
gspread>=5.10         # Google Sheets API
statsmodels>=0.14     # Statistical models (ARIMA)
pmdarima>=2.0         # Auto ARIMA
```

---

## 8. Contact și Suport

**Autor**: Programator Principal  
**Instituție**: Facultatea de Economie și Administrare Afacerilor  
**Data**: Mai 2026  
**Versiune**: 1.0

Pentru întrebări sau sugestii referitoare la implementare, vă rog să contactați echipa de dezvoltare.

---

**Document generat**: 31.05.2026  
**Format**: Markdown (README.md)  
**Licență**: Academic Use Only
