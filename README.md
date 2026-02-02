#  Hotel Reservation Management System

##  Overview
This project is a **personal and cleaned version of an academic hotel reservation system**.  
It demonstrates how to design and deploy a backend-driven application for managing hotels,
rooms, reservations, and partner agencies.

The system combines **Python business logic**, a **Streamlit web interface**, and a **MySQL database**
fully containerized using **Docker**.

---

##  Features
- Hotel room management (single, double, suite)
- Reservation creation and management
- Agency-based booking logic
- Database persistence with MySQL
- Web interface built with Streamlit
- Fully containerized environment using Docker Compose

---

##  Tech Stack
- **Programming Language:** Python  
- **Web Framework:** Streamlit  
- **Database:** MySQL  
- **Query Language:** SQL (DDL & DML)  
- **Containerization:** Docker & Docker Compose  

---

##  Database & SQL
The project uses a MySQL relational database with SQL scripts for schema creation and data initialization.

Implemented SQL operations include:
- `CREATE TABLE` statements for database schema
- Primary and foreign key constraints
- Relational modeling between hotels, rooms, reservations, and agencies
- SQL queries for data insertion and retrieval


```md
Database initialization scripts are located in:

```text
mysql-docker/

---



```md
## 📁 Project Structure

```text
hotel-reservation-project-personal/
│
├── mysql-docker/
│   └── data/
│
├── streamlit-app/
│   ├── assets/
│   ├── pages/
│   ├── styles/
│   ├── app.py
│   ├── db.py
│   ├── utils.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── install_requirements.sh
│
├── docker-compose.yml
├── .gitignore
└── README.md
