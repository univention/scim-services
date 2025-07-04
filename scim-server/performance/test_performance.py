# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import os
import time

import requests
from faker import Faker


fake = Faker()


def run_performance_test() -> None:
    print("\n=== SCIM API Performance Test ===\n")

    scim_server_url = os.getenv("SCIM_SERVER_URL")

    headers = {"Content-Type": "application/json"}

    # Test 1: Create users
    num_users_to_create = [5, 50]
    created_user_ids = []

    for num_users in num_users_to_create:
        start_time = time.time()
        for _i in range(num_users):
            first_name = fake.first_name()
            last_name = fake.last_name()
            test_user_data = {
                "userName": f"{fake.user_name()}_{int(time.time() * 1000)}",  # Add milliseconds for more uniqueness
                "displayName": f"{first_name} {last_name}",
                "name": {"givenName": first_name, "familyName": last_name},
                "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
            }

            user_url = f"{scim_server_url}/Users"
            response = requests.post(user_url, json=test_user_data, headers=headers)

            try:
                response.raise_for_status()  # Raise an exception for HTTP errors
                created_user_ids.append(response.json()["id"])
            except requests.exceptions.HTTPError as e:
                print(f"Failed to create user: {response.status_code} - {response.text}")
                raise e
            except KeyError:
                print(f"Failed to get user ID from response: {response.text}")
                raise

        end_time = time.time()
        time_taken = end_time - start_time
        print(f"Created {num_users} users in {time_taken:.2f} seconds ({num_users / time_taken:.2f} users/second)")

    # Test 2: Modify user descriptions
    start_time = time.time()
    for user_id in created_user_ids:
        patch_url = f"{scim_server_url}/Users/{user_id}"
        patch_data = {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
            "Operations": [{"op": "replace", "path": "displayName", "value": fake.name()}],
        }
        response = requests.patch(patch_url, json=patch_data, headers=headers)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"Failed to modify user {user_id}: {response.status_code} - {response.text}")
            raise e
    end_time = time.time()
    time_taken = end_time - start_time
    print(
        f"Modified {len(created_user_ids)} users in {time_taken:.2f} seconds "
        f"({len(created_user_ids) / time_taken:.2f} users/second)"
    )

    # Test 3: Get all users
    start_time = time.time()
    get_all_users_url = f"{scim_server_url}/Users"
    response = requests.get(get_all_users_url, headers=headers)
    try:
        response.raise_for_status()
        all_users = response.json()["Resources"]
    except requests.exceptions.HTTPError as e:
        print(f"Failed to get all users: {response.status_code} - {response.text}")
        raise e
    except KeyError:
        print(f"Failed to parse all users response: {response.text}")
        raise
    end_time = time.time()
    time_taken = end_time - start_time
    print(
        f"Retrieved {len(all_users)} users in {time_taken:.2f} seconds "
        f"(request time for getting {len(all_users)} users)"
    )

    # Test 4: Delete all users
    start_time = time.time()
    for user_id in created_user_ids:
        delete_url = f"{scim_server_url}/Users/{user_id}"
        response = requests.delete(delete_url, headers=headers)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            print(f"Failed to delete user {user_id}: {response.status_code} - {response.text}")
            # Continue to try deleting other users even if one fails
    end_time = time.time()
    time_taken = end_time - start_time
    print(
        f"Deleted {len(created_user_ids)} users in {time_taken:.2f} seconds "
        f"({len(created_user_ids) / time_taken:.2f} users/second)"
    )


if __name__ == "__main__":
    run_performance_test()
