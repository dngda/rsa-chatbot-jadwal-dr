from typing import Any
from app.api.rsa_client import RSAClient
from app.utils.query_normalizer import normalize_query_with_fallback

rsa = RSAClient()

def search(query: str) -> dict[str, Any]:
    """Search doctors or clinics by keyword.

    Use this when the user mentions a doctor's name, clinic name, or specialty without specifying a date.

    Args:
        query: Doctor name, clinic name, or specialty keyword.
    """

    query_normalization = normalize_query_with_fallback(query)
    primary_result = rsa.search_doctors_or_clinic(
        query_normalization.normalized or query_normalization.original
    )

    if primary_result:
        return primary_result

    if query_normalization.fallback:
        fallback_result = rsa.search_doctors_or_clinic(query_normalization.fallback)
        if fallback_result:
            return fallback_result

    return primary_result


def nearest_schedule(location_id: str) -> dict[str, Any]:
    """Get nearest schedules for a doctor using a location_id.

    Use this when the user wants to find the nearest available appointment for a specific doctor by location_id,
    which is returned from the search() function.

    Args:
        location_id: Location ID returned from search().
    """
    return rsa.get_nearest_schedules_by_location_id(location_id)


def schedule(date: str, query: str) -> dict[str, Any]:
    """Get doctor schedules by date and keyword.

    Use this when the user specifies a date along with a doctor or clinic keyword.
    But if the user only specifies a doctor or clinic without a date, use search() instead.

    Args:
        date: Date in YYYY-MM-DD format.
        query: A doctor or clinic keyword.
    """

    query_normalization = normalize_query_with_fallback(query)
    primary_result = rsa.get_schedules_by_date_and_optional_query(
        date=date,
        query=query_normalization.normalized or query_normalization.original,
    )

    if primary_result:
        return primary_result

    if query_normalization.fallback:
        fallback_result = rsa.get_schedules_by_date_and_optional_query(
            date=date,
            query=query_normalization.fallback,
        )
        if fallback_result:
            return fallback_result

    return primary_result

RSA_TOOLS = [search, nearest_schedule, schedule]