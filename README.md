# Cargo Claims Manager

<p align="center">
<img width="420" alt="Cargo Claims Manager Logo" src="https://github.com/user-attachments/assets/72ca6f2f-4f4b-4a9a-b2ce-0d896e474472" />
</p>

<p align="center">
  <b>Enterprise Cargo Insurance & Claims Management Platform</b><br>
  Built with Streamlit, SQL Server, and Python for real-world airline cargo operations.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg"/>
  <img src="https://img.shields.io/badge/Streamlit-Framework-red.svg"/>
  <img src="https://img.shields.io/badge/SQL%20Server-Database-darkgreen.svg"/>
  <img src="https://img.shields.io/badge/Status-Production-success.svg"/>
</p>

---

# Overview

Cargo Claims Manager is a professional cargo insurance and claims handling platform developed for real operational use within a global cargo and airline environment.

The system centralizes the complete cargo claims workflow including:

* Insurance claim registration
* Cargo damage/loss tracking
* Attachment and documentation management
* Compensation calculation
* Exchange rate conversion
* Reporting and analytics
* User activity logging
* Administrative access control

The project was designed and implemented as a real-world operational solution for a global cargo company environment, focusing on workflow efficiency, data organization, reporting, and usability for claims teams.

---

# Highlights

* Real-world production-oriented project
* Designed for cargo operations workflow efficiency
* Enterprise-style reporting system
* SQL Server integration
* Interactive analytics dashboard
* File storage and preview system
* Administrative management tools
* Operational audit logging
* Clean and responsive UI

---

# Key Features

### 1- Claims Management

* Create, update, search, and delete insurance claims
* Automated insurance number formatting
* AWB validation and shipment tracking
* Route and sector management
* Commodity classification
* Parcel damage/loss tracking
* Claim status handling
* Compensation request and acceptance workflow


### 2- Attachment Management

* Upload supporting claim documents
* Store files directly inside SQL Server database
* Preview PDFs and images inside the application
* Download and delete attachments
* Department-based attachment categorization
* Sent/Received date tracking


### 3- Reporting & Analytics

* Dynamic filtering system
* Excel report generation
* PDF report export
* Interactive dashboards
* Country/location analytics
* Damage ratio analysis
* Trend visualization
* Aggregation and grouping tools
* Custom chart builder using Plotly


### 4- Financial Operations

* Multi-currency support
* Live exchange rate conversion
* EGP and USD compensation calculations
* Requested vs accepted compensation tracking


### 5- Security & Administration

* User authentication system
* Role-based permissions
* User activity logging
* Administrative user management
* Restricted admin-only operations

---

# Tech Stack

| Technology | Purpose                       |
| ---------- | ----------------------------- |
| Python     | Core backend logic            |
| Streamlit  | Frontend framework            |
| SQL Server | Database system               |
| SQLAlchemy | Database ORM/queries          |
| Pandas     | Data processing               |
| Plotly     | Analytics & visualizations    |
| OpenPyXL   | Report generation             |
| Requests   | Exchange rate API integration |

---

# System Architecture

```text
Frontend (Streamlit UI)
        │
        ▼
Business Logic Layer (Python)
        │
        ▼
SQL Server Database
        │
        ├── Claims
        ├── Attachments
        ├── Users
        ├── Logs
        └── Reference Tables
```

---

# Main Modules

### 1- Insurance Claims

Handles complete cargo insurance claim lifecycle management.

#### Includes:

* Claim registration
* AWB information
* Cargo details
* Compensation workflow
* Status tracking
* Notes & history


### 2- Attachments System

Manages operational claim documentation.

#### Supported Operations:

* Upload
* Preview
* Download
* Delete
* Categorization


### 3- Dashboard & Reports

Provides operational analytics and business intelligence.

#### Includes:

* Interactive filtering
* Data exports
* Charts and diagrams
* KPI analysis
* Aggregation tools


### 4- Administration

Administrative management interface.

#### Includes:

* User management
* Permissions handling
* Activity logs
* Access control

---

# Screenshots

### Claims Page
<img width="1366" height="588" alt="Claims Page" src="https://github.com/user-attachments/assets/7dbaeaf4-4905-4c04-9493-facc6c3cf0ea" />

### Claims Functions & Attachments Section
<img width="1366" height="651" alt="Claims Functions & Attachments Section" src="https://github.com/user-attachments/assets/9e5d39f5-3542-431e-9b12-4e8b2dc946bb" />
<br>

### Claims Dashboard

### Claims Table
<img width="1366" height="651" alt="Claims Table" src="https://github.com/user-attachments/assets/ca98433b-71a4-424e-98f5-d825694c539d" />
<br>

### Analytics & Visualizations
<img width="1366" height="651" alt="Analytics & Visualizations" src="https://github.com/user-attachments/assets/d0c90590-583b-409b-a542-f0bb3b3a129a" />
<br>

### Custom Chart Builder (Treemap)
<img width="1366" height="651" alt="Custom Chart Builder (Treemap)" src="https://github.com/user-attachments/assets/567bbf4d-ad5e-4ac2-9814-ba626575ba59" />
<br>

### Aggregation & Grouping functions
<img width="1366" height="651" alt="Aggregation & Grouping" src="https://github.com/user-attachments/assets/eafaf982-ee75-46c8-800b-c8f52d160e2e" />

---

# Database Setup

Restore the provided SQL Server backup in the ***``Config``*** folder:

```text
CCMDB.bak
```

---

# Database Configuration

Before running the application, configure:

```ini
db_config.txt
```

Example:

```ini
DRIVER=ODBC Driver 17 for SQL Server
SERVER=YourServerName\InstanceName
DATABASE=CCMDB
TRUSTED_CONNECTION=yes
```

---

# Running the Application

### First of all - Install dependencies:

```bash
pip install -r requirements.txt
```

### Option 1 — Batch File

Run:

```text
CCM Run.bat
```

### Option 2 — Manual Execution

Run Streamlit:

```bash
streamlit run app.py
```

---

# Default Login

```text
Username: Admin
Password: Admin
```

---

# Project Structure

```text
CargoClaimsManager/
│
├── App_Pages/
│   ├── insurance_claim.py
│   ├── insurance_claim_mail.py
│   ├── login.py
│   ├── logs.py
│   ├── reports.py
│   └── reports_mail.py
│
├── Core/
│   ├── DB_Connection.py
│   ├── functions.py
│   └── functions_mail.py
│
├── Assets/
│   ├── insurance_icon.ico
│   └── Cargo_Claims_Manager_Blue_logo.png
│
├── Config/
│   ├── db_config.txt
│   └── CCMDB.bak
│
├── app.py
├── CCM Run.bat
└── requirements.txt
```

---


<p align="center">
Enterprise software developed for real-world cargo operations.
  <br>
  © 2026 Ahmed Shoeb
</p>
