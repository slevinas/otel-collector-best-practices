
### 📁 Project Folder Structure – xplg-api-benchmaker-runner
xplg-api-benchmaker-runner/ 
│ 
├── api_fastapi/                 # 🚀 FastAPI application with decorated endpoints 
│ ├── scriptA_api_psql.py.       # Main FastAPI server (handles login, /store, /math, etc.) 
│ ├── db/                        # DB models and decorators 
│ │ ├── models.py                # SQLAlchemy models: ApiBenchmarkLog, StoredResource 
│ │ ├── api_monitor_decorator.py # Decorator to log request/response benchmarks 
│ │ └── api_handlers.py          # Optional: endpoint logic 
│ ├── benchmark/                 # 🧠 Benchmarking SDK and test harness 
│ ├── sdk_api_wrapper/           # Client SDK wrapper (to test API endpoints) 
│ │ └── json_key_reader_benchmaker_sdk.py # Client class for interacting with the API 
│ ├── sdk_runner.py              # CLI tool to run SDK-based benchmark tests 
│ ├── db_models.py               # SDK-side Benchmark table model (SQLAlchemy) 
│ ├── db_orm/                    # 🛢️ DB initialization and engine configuration 
│ ├── db.py                      # SQLAlchemy engine and session creator 
│ ├── base.py                    # Declarative Base for all ORM models 
│ └── init_db.py                 # CLI tool to init (drop/create) tables 
│ ├── utils/                     # 🔧 Helpers and logic extractors 
│ ├── scriptB.py                 # Vector math logic on stored JSON resources 
│ └── extract_value_from_json.py # Safe JSON path key extractors 
│ ├── benchmarks/               # 🗃️ JSON files used for local benchmark diffing 
│ └── *.json                    # Saved result snapshots from SDK test runs 
│ ├── .env                      # Environment file with DB creds, etc. 
├── docker-compose.yml          # Optional: PG container or stack setup 
├── pyproject.toml / poetry.lock # Project dependencies and virtual env config 
└── README.md / CHANGELOG.md    # 📘 Docs and update history
