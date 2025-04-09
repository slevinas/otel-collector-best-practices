### To test the loging and run multiple concurent and requests per user :

```commandline
 poetry run python ./benchmaker/sdk_api_wrapper/simulate_login_benchmark.py 2 3 

📢 Initiating login request...
📢 Initiating login request...
User 2 login 1 completed in 0.1182 seconds
📢 Initiating login request...
User 1 login 1 completed in 0.1840 seconds
📢 Initiating login request...
User 2 login 2 completed in 0.0218 seconds
📢 Initiating login request...
User 1 login 2 completed in 0.0258 seconds
📢 Initiating login request...
User 2 login 3 completed in 0.0275 seconds
User 1 login 3 completed in 0.0273 seconds

--- Overall Login Benchmark ---
Total login requests: 6
Overall average login time: 0.0674 seconds

```