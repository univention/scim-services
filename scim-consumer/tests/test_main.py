from univention.scim.consumer import scim_client


def test_scim_create_user(scim_consumer, udm_user):
    
    config = scim_client.get_config()
    client = scim_client.get_client(config)
    user = scim_client.get_user_by_username(client, udm_user.get("username"))
    
    assert user.user_name == udm_user.get("username")