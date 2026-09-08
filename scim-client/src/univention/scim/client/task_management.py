# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025-2026 Univention GmbH

"""Inspect and manage the SCIM Client database, based on the OX Connector task-management CLI."""

import inspect
import json
import os
from argparse import ArgumentParser, Namespace, RawTextHelpFormatter
from collections.abc import Callable
from functools import partial
from typing import Any

from univention.provisioning.error_handling.db import DBSession, Old


def _call(func: Callable[..., None], args: Namespace) -> None:
    params = vars(args).copy()
    params.pop("func")
    with DBSession(os.environ["PROVISIONING_DB"]) as db:
        func(db, **params)


def _add_action(subparsers: Any, func: Callable[..., None]) -> None:
    name = func.__name__.replace("_", "-")
    description = func.__doc__
    subparser = subparsers.add_parser(name, description=description, help=description)
    for name, param in inspect.signature(func).parameters.items():
        if name == "db":
            continue

        arg_params: dict[str, Any] = {"required": param.default is inspect.Parameter.empty}
        if not arg_params["required"]:
            arg_params["default"] = param.default
        if param.annotation is bool:
            arg_params["action"] = "store_true"
        elif param.annotation is int:
            arg_params["type"] = int
        subparser.add_argument(f"--{name.replace('_', '-')}", **arg_params)
    subparser.set_defaults(func=partial(_call, func))


def show_item(db: DBSession, obj_id: str, output_format: str = "simple") -> None:
    """Show an object's entries in old, tasks and morgue (simple or json)."""
    db.show_item(obj_id, output_format)


def summarize_tasks(db: DBSession, output_format: str = "simple") -> None:
    """Summarize pending tasks (simple or json)."""
    db.summarize_tasks(output_format)


def summarize_morgue(db: DBSession, output_format: str = "simple") -> None:
    """Summarize failed tasks (simple, fuller or json)."""
    db.summarize_morgue(output_format)


def search_tasks(db: DBSession, first: bool = False) -> None:
    """Show pending tasks, or only the first task with --first."""
    for task in db.get_tasks():
        print("DN:", task.dn)
        print("Object Identifier:", task.obj_id)
        print("UDM module:", task.udm_module)
        print("ID (database):", task.id)
        print("Created at:", task.created_at)
        print("Status:", task.status)
        print("Error count:", task.num_errors)
        if task.attrs:
            print("Attributes:")
            for name, value in sorted(json.loads(task.attrs).items()):
                print(" ", name, ":", value)
        print("-")
        if first:
            break


def search_old(db: DBSession, obj_id: str) -> None:
    """Show the last successfully synced state. Use '*' in --obj-id to match multiple objects."""
    obj_id = obj_id.replace("*", "%")
    olds = db.session.query(Old).filter(Old.obj_id.like(obj_id)).all()
    for old in olds:
        print("DN:", old.dn)
        print("Object Identifier:", old.obj_id)
        print("UDM module:", old.udm_module)
        print("ID (database):", old.id)
        print("Attributes:")
        for name, value in sorted(json.loads(old.attrs).items()):
            print(" ", name, ":", value)
        print("-")


def search_morgue(db: DBSession, obj_id: str = "*") -> None:
    """Show failed tasks and their tracebacks, optionally filtered by --obj-id."""
    for error in db.get_errors(obj_id=obj_id):
        print("DN:", error.dn)
        print("Object Identifier:", error.obj_id)
        print("UDM module:", error.udm_module)
        print("ID (database):", error.id)
        print("Error occurred:", error.timestamp)
        print("Error:", error.error_msg)
        print("-")


def retry_from_morgue(db: DBSession, obj_id: str) -> None:
    """Requeue all matching failed changes using their stored attributes.

    Stored attributes may overwrite newer state; check before retrying.
    Requeuing keeps the Morgue entries. After a successful create or update,
    the client removes all Morgue entries for that object.
    Processing resumes on the next message, client startup or active network-retry iteration.
    Restart an idle client to process the queued tasks without a new message.
    """
    db.retry_from_morgue(obj_id)


def remove_from_morgue(db: DBSession, obj_id: str) -> None:
    """Remove all matching Morgue entries, not the objects in SCIM or UDM."""
    db.remove_from_morgue(obj_id)


def move_task_to_morgue(db: DBSession, task_id: int, error_msg: str) -> None:
    """Move a pending task to the Morgue with a reason for manual investigation.

    Stop the client first if it is currently processing this task.
    This does not cancel an in-flight request or interrupt a retry wait.
    """
    db.move_task_to_morgue(task_id, error_msg)


def run() -> None:
    parser = ArgumentParser(
        description="""Inspect and manage the SCIM Client database selected by PROVISIONING_DB.
tasks: Pending changes waiting to be synchronized.
old: The last successfully synchronized state of each object.
morgue: Failed changes that need to be examined by an administrator.""",
        formatter_class=RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(
        description="Use %(prog)s <action> --help for further help and available arguments.",
        metavar="action",
    )
    _add_action(subparsers, show_item)
    _add_action(subparsers, summarize_tasks)
    _add_action(subparsers, summarize_morgue)
    _add_action(subparsers, search_tasks)
    _add_action(subparsers, search_old)
    _add_action(subparsers, search_morgue)
    _add_action(subparsers, retry_from_morgue)
    _add_action(subparsers, remove_from_morgue)
    _add_action(subparsers, move_task_to_morgue)

    args = parser.parse_args()
    if not getattr(args, "func", None):
        parser.print_help()
    else:
        if not os.environ.get("PROVISIONING_DB"):
            parser.error("PROVISIONING_DB must be set to the SCIM Client database connection string.")
        args.func(args)


if __name__ == "__main__":
    run()
