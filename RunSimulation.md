### 1. Run Basic Experiments

Before adding any further complexity or session tagging, run the load simulation with a few different parameter combinations. For example:

Default Test:
Run with the default parameters to simulate a small number of users and cycles:

```commandline
python async_sdk_runner.py
```

This will simulate the default 5 users each running 3 cycles with no delay. 
You should see output indicating that each user completed its cycles 
and a final overall summary with total and average times.

Increased Users:
Simulate more concurrent users to see how the system behaves:


``
python async_sdk_runner.py --users 10 --requests-per-user 3
``

Watch that all users are simulated concurrently; 
the overall summary should correctly aggregate the timings from each simulated user.

Varying Request Counts and Delays:
Test with different numbers of request cycles and a delay between cycles 
to mimic more realistic usage:

```commandline
python async_sdk_runner.py --users 5 --requests-per-user 5 --delay 0.5
```

**Check that each cycle’s elapsed time reflects the delay and that the summary 
correctly computes average times.**

### 2. Validate Output Metrics
Examine the output printed by the load runner. It should include:

- *A line for each simulated user indicating when the user starts and completes each cycle 
with an elapsed time.*

- *A final overall summary that shows:*

- _Total users simulated._

- _Total number of cycles performed._

- _Combined total time across all users._

- _Overall average time per cycle._

**For instance, the output might look similar to:**

🚀 Starting user 1
🔄 User 1 cycle 1: completed in 0.3456s
🔄 User 1 cycle 2: completed in 0.3333s
...
✅ User 1 completed 3 cycles in 1.0500s (avg 0.3500s)

...

📊 Overall Summary:
- Total users simulated: 5
- Total cycles performed: 15
- Combined total time: 5.2500s
- Overall average time per cycle: 0.3500s
- 
Make sure that the timings and counts add up according to the parameters you provided.

### 3. Check API Behavior

**Since the load simulation is making real API calls:**

- Monitor the FastAPI Logs:
 - Keep an eye on your FastAPI server logs to ensure that all endpoints are being hit and handled without errors. Look for any unusual delays or errors that might indicate resource contention or issues with the asynchronous handling.

- Database Records:
  - If your API is set up to log benchmark records to PostgreSQL 
  - (via your async benchmark insertions), query the benchmarks or api_monitor tables
  - to verify that entries are being logged for each simulated request. 
  - This helps confirm the load testing simulation is actively interacting with the API 
  - and recording performance data.

### 4. Automated Testing for Consistency
#### Repeated Runs:

- Execute the load simulation several times with the same parameters and 
- compare the overall summary metrics. 
- While slight variations are normal, the aggregate performance and per-cycle timings 
- should remain within a predictable range.

#### Edge Cases:
##### Test edge cases such as:

- Very high user counts or requests per user (if your machine can handle it) 
- to see if any resource exhaustion issues occur.

- Using a non-zero delay to check that delays are properly incorporated in the cycle timings.

#### Error Handling:

- Try simulating a slight API failure (for example, temporarily stop the API service) 
- to see if your load runner gracefully handles errors or records the failure in the logs.

### 5. Considerations for Session Tagging
- For now, since all simulated users use the same credentials, 
- focus on ensuring that the parameters, timers, and aggregated metrics work reliably. 
- Once you’re satisfied with the basic load testing results, adding user session tagging 
- can be done to correlate individual requests with a unique user or session identifier. 
- This is best done after confirming that your primary load testing setup is robust.