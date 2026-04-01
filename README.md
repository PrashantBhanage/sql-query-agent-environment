---
title: SQL Query Agent Environment
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: python
sdk_version: "" # Python spaces use latest installed runtime
python_version: "3.10"
app_file: app.py
pinned: false
---

# SQL Query Agent Environment

A minimal but fully working SQL Query Agent Environment for hackathon validation with OpenEnv-compatible endpoints.

## Project Structure

```
.
├── Dockerfile              # Docker container configuration
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── openenv.yaml           # OpenEnv configuration
├── app.py                 # Gradio UI application
├── inference.py           # Main inference module
├── baseline_inference.py  # Baseline inference module
├── models.py              # Pydantic models
├── ecommerce.db           # SQLite database (auto-created)
├── __init__.py            # Package init
├── server/
│   ├── __init__.py
│   └── app.py             # FastAPI application
└── tests/
    └── test_smoke.py      # Smoke tests
```

## Features

- SQLite-backed ecommerce database with sample data
- OpenEnv-compatible reset/step/state API
- FastAPI application with health checks
- Read-only SQL query execution
- Automatic database initialization

## How to Run Locally

### 1. Create and Activate Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Server

```bash
uvicorn server.app:app --host 0.0.0.0 --port 7860
```

Or run directly with Python:

```bash
python -c "from server.app import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=7860)"
```

### 4. Test Endpoints with curl

```bash
# Health check
curl -X GET http://localhost:7860/health

# Get state
curl -X GET http://localhost:7860/state

# Reset environment
curl -X POST http://localhost:7860/reset \
  -H 'Content-Type: application/json' \
  -d '{"task_id":"task_1"}'

# Execute SQL query
curl -X POST http://localhost:7860/step \
  -H 'Content-Type: application/json' \
  -d '{"query":"SELECT COUNT(*) FROM customers;","task_id":"task_1"}'
```

### 5. Run openenv validate

```bash
source .venv/bin/activate
openenv validate
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root response |
| `/health` | GET | Health check |
| `/state` | GET | Get current environment state |
| `/reset` | POST | Reset environment and get task info |
| `/step` | POST | Execute SQL query and get observation |
| `/docs` | GET | FastAPI auto documentation |

## Deploy to Hugging Face Spaces

### Option 1: Using Hugging Face CLI

```bash
# Install huggingface_hub
pip install huggingface_hub

# Login
huggingface-cli login

# Create space
huggingface-cli create-repo sql-query-agent --type space

# Clone and push
git clone https://huggingface.co/spaces/YOUR_USERNAME/sql-query-agent
cd sql-query-agent
# Copy all files from this repo
git add .
git commit -m "Initial commit"
git push
```

### Option 2: Using Docker on HF Spaces

1. Create a new Space on Hugging Face
2. Select "Docker" as the SDK
3. Add your Dockerfile and requirements.txt
4. HF will automatically build and deploy

## Database Schema

The environment includes an ecommerce database with these tables:

- **customers**: Customer information
- **categories**: Product categories
- **products**: Product catalog
- **orders**: Customer orders
- **order_items**: Individual order items

## Task Examples

| Task ID | Description |
|---------|-------------|
| task_1 | Count total customers |
| task_2 | Find products with price > 50 |
| task_3 | Calculate revenue from completed orders |
| task_4 | List top 3 customers by order count |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DB_PATH | ecommerce.db | Path to SQLite database |

## License

MIT
