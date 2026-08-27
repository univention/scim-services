# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import asyncio
from pathlib import Path

import httpx
import pytest

from univention.provisioning.error_handling.db import Base, DBSession, engine, initialize_db
from univention.scim.client.authentication import AuthMethod
from univention.scim.client.scim_client import ScimConsumer
from univention.scim.client.scim_client_settings import ScimConsumerSettings

from ..data.provisioning_message_factory import get_provisioning_message


@pytest.fixture(autouse=True, scope="module")
def delete_db():
    yield
    if engine.url.drivername == "sqlite":
        Path(engine.url.database).unlink()


@pytest.fixture(autouse=True)
def clean_db():
    initialize_db()
    yield
    Base.metadata.drop_all(engine)


def get_consumer(monkeypatch):
    settings = ScimConsumerSettings(
        scim_server_base_url="http://localhost",
        scim_auth_method=AuthMethod.NONE,
    )
    consumer = ScimConsumer(scim_http_client=object(), group_membership_resolver=object(), settings=settings)

    calls = {"write": [], "delete": []}

    def write_udm_object(udm_object, topic):
        calls["write"].append((topic, udm_object))

    def delete(udm_object, topic):
        calls["delete"].append((topic, udm_object))

    monkeypatch.setattr(consumer, "write_udm_object", write_udm_object)
    monkeypatch.setattr(consumer, "delete", delete)

    return consumer, calls


def test_handle_udm_message_create_moves_task_to_old(monkeypatch):
    consumer, calls = get_consumer(monkeypatch)

    asyncio.run(consumer.handle_udm_message(get_provisioning_message("user_create")))

    assert len(calls["write"]) == 1
    assert calls["write"][0][0] == "users/user"

    with DBSession() as db:
        assert not db.contain_tasks()
        old = db.get_old(None, "ffffffff-ffff-ffff-ffff-ffffffffffff")
        assert old is not None
        assert old.dn == "uid=testuser,cn=users,dc=univention-organization,dc=intranet"


def test_handle_udm_message_delete_removes_old(monkeypatch):
    consumer, calls = get_consumer(monkeypatch)

    asyncio.run(consumer.handle_udm_message(get_provisioning_message("user_create")))
    asyncio.run(consumer.handle_udm_message(get_provisioning_message("user_delete")))

    assert len(calls["write"]) == 1
    assert len(calls["delete"]) == 1
    assert calls["delete"][0][0] == "users/user"

    with DBSession() as db:
        assert not db.contain_tasks()
        assert db.get_old(None, "ffffffff-ffff-ffff-ffff-ffffffffffff") is None


def test_handle_udm_message_error_moves_task_to_morgue(monkeypatch):
    consumer, calls = get_consumer(monkeypatch)
    monkeypatch.setattr(
        consumer,
        "write_udm_object",
        lambda udm_object, topic: (_ for _ in ()).throw(ValueError("boom")),
    )

    asyncio.run(consumer.handle_udm_message(get_provisioning_message("user_create")))

    with DBSession() as db:
        assert not db.contain_tasks()
        errors = list(db.get_errors("ffffffff-ffff-ffff-ffff-ffffffffffff"))
        assert len(errors) == 1
        assert "boom" in errors[0].error_msg


def test_handle_udm_message_http_error_moves_task_to_morgue(monkeypatch):
    consumer, calls = get_consumer(monkeypatch)
    monkeypatch.setattr(
        consumer,
        "write_udm_object",
        lambda udm_object, topic: (_ for _ in ()).throw(httpx.ConnectError("connection refused")),
    )

    asyncio.run(consumer.handle_udm_message(get_provisioning_message("user_create")))

    with DBSession() as db:
        assert not db.contain_tasks()
        errors = list(db.get_errors("ffffffff-ffff-ffff-ffff-ffffffffffff"))
        assert len(errors) == 1
        assert "connection refused" in errors[0].error_msg


def test_handle_udm_message_invalid_realm_raises(monkeypatch):
    consumer, calls = get_consumer(monkeypatch)

    message = get_provisioning_message("user_create")
    message.realm = "invalid"

    with pytest.raises(ValueError):
        asyncio.run(consumer.handle_udm_message(message))


def test_handle_udm_message_unknown_topic_is_skipped(monkeypatch):
    consumer, calls = get_consumer(monkeypatch)
    consumer.settings.modules = ["groups/group"]

    asyncio.run(consumer.handle_udm_message(get_provisioning_message("user_create")))

    assert not calls["write"]
    assert not calls["delete"]
    with DBSession() as db:
        assert not db.contain_tasks()
