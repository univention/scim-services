# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import threading
from time import sleep


def infinity_proc():
    max = 3
    count = 0
    while True:
        print("Hello!")
        sleep(2)
        count += 1
        if count >= max:
            break


def start_proc():
    print("start_proc started")
    thread = threading.Thread(target=infinity_proc())
    thread.setDaemon(True)
    thread.start()
    print("start_proc yield before")
    yield
    print("start_proc yield after")
    thread.join()
    print("start_proc stopped.")


print("Test started")
start_proc()
sleep(5)
print("Test stopped")
