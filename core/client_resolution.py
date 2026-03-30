"""Client lookup helpers used by UI callbacks."""


def resolve_client_id_by_name(clients, client_name):
    """Resolve a client id from a client name using client rows."""
    for client in clients:
        if client[1] == client_name:
            return client[0]
    return None

