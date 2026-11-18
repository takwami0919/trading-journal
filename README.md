# Trading Journal

A full-stack trading journal application that integrates with the Alpaca Paper Trading API to import trading executions, track positions, and visualize trading performance.

Built with **Next.js, TypeScript, Python, FastAPI, and PostgreSQL**.

## Features

### Trading Dashboard
- View trade history and overall performance statistics
- Track total trades, win rate, and realized profit/loss
- Visualize cumulative trading performance with interactive charts
- Navigate to individual trade details

### Alpaca API Integration
- Connect to Alpaca's paper-trading environment
- Import executed buy and sell orders through REST APIs
- Store execution data in PostgreSQL
- Prevent duplicate execution imports using database constraints
- Process trades using FIFO matching logic

### Trade Details
- View entry and exit prices
- Track position quantities and trade status
- Review execution timestamps and calculated profit/loss

### Interactive Demo Mode
- Explore six simulated trades without connecting to a brokerage account
- View simulated performance analytics and trade history
- Open individual trade-detail pages
- Edit trading strategies, notes, and lessons learned
- Save demo notes using browser local storage
- Switch between simulated data and Alpaca paper-trading data

Demo Mode is clearly identified and does not modify actual broker records.

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | Next.js, React, TypeScript |
| Styling | Tailwind CSS |
| Charts | Recharts |
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Database Migrations | Alembic |
| Broker Integration | Alpaca Paper Trading REST API |
| Version Control | Git, GitHub |

## System Architecture

```text
Next.js Frontend
       |
       | HTTP / JSON
       v
FastAPI Backend
       |
       +---- PostgreSQL Database
       |
       +---- Alpaca Paper Trading API

Demo Mode
       |
       +---- Simulated Frontend Data
       |
       +---- Browser Local Storage (Journal Notes)
```

The frontend communicates with a Python FastAPI backend through HTTP requests.

The backend retrieves trading activity from Alpaca, processes execution records, and stores trading data in PostgreSQL.

Demo Mode operates independently using simulated frontend data.

## Project Structure

```text
trading-journal/
├── backend/
│   ├── app/
│   │   ├── adapters/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   └── services/
│   ├── alembic/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx
│   │   │   └── trades/
│   │   └── components/
│   └── package.json
│
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

- Python 3
- Node.js and npm
- PostgreSQL
- Alpaca Paper Trading account (for live broker imports)

### 1. Clone the Repository

```bash
git clone https://github.com/takwami0919/trading-journal.git
cd trading-journal
```

### 2. Set Up the Backend

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file based on `.env.example`, then configure the PostgreSQL connection and required secrets.

Run database migrations:

```bash
python -m alembic upgrade head
```

Start the backend:

```bash
python -m uvicorn app.main:app --reload
```

The API will be available at:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

### 3. Set Up the Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open:

`http://localhost:3000`

### 4. Explore Demo Mode

Open:

`http://localhost:3000/?mode=demo`

Demo Mode provides simulated trading data and does not require a running backend.

Click a trade symbol to see its details and edit its journal notes.

## API Examples

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/trades/` | Retrieve trades |
| GET | `/trades/{trade_id}` | Retrieve trade details |
| GET | `/executions/` | Retrieve execution history |
| POST | `/executions/sync` | Synchronize Alpaca executions |
| GET | `/analytics/summary` | Retrieve dashboard statistics |
| GET | `/analytics/performance` | Retrieve trading performance data |

## Current Development Status

The application includes a functional demo dashboard, interactive performance charts, trade-detail pages, and editable demo journal notes.

Alpaca paper-trading execution imports are implemented. Full reconciliation of crypto trading fees, partial position closures, and live realized P&L remains under development.

Additional planned improvements include persistent journal editing for live trades, enhanced analytics, and deployment.

## Security

- API credentials are configured through environment variables.
- Sensitive `.env` files are excluded from version control.
- Broker credentials are encrypted when stored by the backend.
- Demo Mode does not submit brokerage orders or modify real trading data.

**This project is intended for educational and portfolio demonstration purposes. Demo trades and performance results are simulated and do not represent actual investment returns.**