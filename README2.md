📁 xplg-api-benchmaker-runner/
├── api_fastapi/               # FastAPI app with monitoring & benchmarking decorators
│   ├── scriptA_api_psql.py    # Main FastAPI server
│   └── api_monitor_decorator.py  # Decorator to track API request timings
├── benchmaker/
│   ├── sdk_api_wrapper/
│   │   ├── json_key_reader_benchmaker_sdk.py  # Old synchronous SDK
│   │   ├── async_sdk_benchmaker_client.py     # ✅ Async SDK for benchmarking
│   │   ├── async_sdk_runner.py                # Manual test runner (PoC)
│   │   └── load_test_runner.py (🆕 planned)    # Future: Concurrency load tester
│   └── db/
│       ├── db_handlers.py      # DB logic for inserting benchmark records
│       ├── bench_models.py     # SQLAlchemy models (Benchmark table)
│       └── db.py               # get_db(), engine setup
├── benchmarks/                # Saved benchmark JSONs
├── docker-compose.yml         # PostgreSQL container (optional)
├── README.md
└── pyproject.toml