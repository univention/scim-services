# SCIM API Performance Test Results (MS1)

## Date of Test

June 30, 2025

## Environment

- Operating System: Linux
- Test Runner: Standalone Python script (`test_performance.py`)
- Target: SCIM API on gaia cluster

## How to Run Performance Tests

1. **Deploy Umbrella Helm Chart:**
    Ensure the umbrella Helm chart is deployed with the following configuration for `nubusScimServer`:

    ```yaml
    nubusScimServer:
      enabled: true
      config:
        auth:
          enabled: false
      docu:
        enabled: true
    ```

2. **Set PATCH_ENABLED Environment Variable:**
    Set the environment variable `PATCH_ENABLED=true` in the `scim-server` deployment and restart the deployment.

3. **Set SCIM_SERVER_URL:**
    Before running the script, set the following environment variable:

    ```bash
    export SCIM_SERVER_URL="https://scim.cgarcia.univention.dev/scim/v2" # Replace with your SCIM server URL
    ```

4. **Run the Script:**

    ```bash
    python test_performance.py
    ```

## Performance Metrics

### User Creation

- Created 5 users in 9.19 seconds (0.54 users/second)
- Created 50 users in 90.92 seconds (0.55 users/second)

### User Modification (Description)

- Modified 55 users in 46.76 seconds (1.18 users/second)

### Get All Users

- Retrieved 111 users in 4.19 seconds (request time for getting 111 users)

### User Deletion

- Deleted 55 users in 43.60 seconds (1.26 users/second)
