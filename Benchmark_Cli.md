### How to Test This in Your CLI
- Single Endpoint Benchmark:

- For the /login endpoint, run:


```poetry run python benchmark_cli.py benchmark --endpoint "/login" --users 2 --requests-per-user 5```

Check that the benchmark for /login executes and that you see your login simulation’s output.

- *Store Endpoint Benchmark:*

- For the /store endpoint with a custom payload:

```commandline
poetry run python benchmark_cli.py benchmark --endpoint "/store" \
 --users 2 --requests-per-user 5 --payload '{"x": {"value": 10}, "y": {"value": 20}}'
```

Verify that the simulated store benchmark prints its output with the supplied payload.

Vector Math Benchmark – Auto-generated Mode:

Run with auto-generated resource names using random payloads (with verification):

```
poetry run python benchmark_cli.py benchmark --endpoint "/run_vectorized_math" \
                   --users 2 --requests-per-user 5 --random --verify --vm-operation "add"

```
We should see that for each cycle, unique resource names are generated, payloads are created and stored, the vector math call is made, and the result is verified.

Vector Math Benchmark – Supplied Resource Names Mode:

If we already have resources (e.g., "A" and "B") created in your system, run:

```commandline
poetry run python benchmark_cli.py benchmark --endpoint "/run_vectorized_math" \
                --users 2 --requests-per-user 5 --resource-names '["A","B"]'

```
- In this case, the benchmark will skip the store calls and simply call run_math on the supplied resources.

### **Run All Endpoints:**

- Test with the --run-all flag:

```commandline
poetry run python benchmark_cli.py benchmark --endpoint "/run_vectorized_math" \
                    --users 2 --requests-per-user 5 --resource-names '["A","B"]'

poetry run python benchmark_cli.py benchmark --run-all --users 2 --requests-per-user 3
```

This should sequentially run the benchmark for /login, /store, and /run_vectorized_math, displaying the results for each.

Final Notes
Make sure your API server is running and accessible at the configured base URL (http://127.0.0.1:8010).

This CLI tool unifies all your benchmarking functions and enables you to easily test individual endpoints or all endpoints together.

You can further expand your CLI (e.g., by adding additional commands or more detailed reporting) as needed.