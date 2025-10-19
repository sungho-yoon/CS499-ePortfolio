def whitelist_filters(filters: dict) -> dict:
    safe = {}
    if not filters:
        return safe
    for k, v in filters.items():
        if k in ALLOWED_FIELDS and v is not None:
            safe[k] = v
    return safe
