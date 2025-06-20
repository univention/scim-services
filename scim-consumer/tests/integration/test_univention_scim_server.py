# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

# @pytest.fixture(scope="session")
# def scim_maildomain(scim_udm_client):
#     name = "scim-consumer.unittests"
#     domains = scim_udm_client.get("mail/domain")
#     if maildomains := list(domains.search(f"name={name}")):
#         maildomain = domains.get(maildomains[0].dn)
#         logger.info(f"Using existing mail domain {maildomain!r}.")
#     else:
#         maildomain = domains.new()
#         maildomain.properties.update({"name": name})
#         maildomain.save()
#         logger.info(f"Created new mail domain {maildomain!r}.")

#     yield name

#     maildomain.delete()
#     logger.info(f"Deleted mail domain {maildomain!r}.")


# @pytest.fixture(scope="session")
# def scim_udm_client() -> UDM:
#     logger.info("Create SCIM udm_client.")
#     udm = UDM.http(os.environ["SCIM_UDM_BASE_URL"], os.environ["SCIM_UDM_USERNAME"], os.environ["SCIM_UDM_PASSWORD"])

#     return udm


def test_fake_test():
    """
    Test that is always false, to check if the Gitlab
    pipeline is working again.
    """
    raise AssertionError()
