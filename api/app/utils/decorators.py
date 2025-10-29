"""
Pagination utility for FastAPI endpoints.

This module provides a decorator function to handle pagination of list-based
responses in FastAPI, ensuring that large datasets are efficiently divided into
manageable chunks.
"""
from fastapi import HTTPException, status
from functools import wraps
from math import ceil
from typing import Any, Callable


def paginate(response_model: Callable[..., Any]):
    """
    Decorator to paginate a list of items returned by a FastAPI endpoint.

    This decorator enables pagination for endpoints that return a list of items.
    It slices the list based on the `page` and `limit` query parameters and
    wraps the response in a specified response model with pagination metadata.

    Args:
        response_model (Callable[..., Any]): A callable that defines the structure
            of the response, typically a Pydantic model with fields for items
            and pagination metadata.

    Returns:
        Callable: A wrapper function that adds pagination to the decorated function.

    Raises:
        HTTPException: If `page` or `limit` query parameters are less than 1.

    Example:
        Define a Pydantic response model:
        ```
        from pydantic import BaseModel
        from typing import List, Dict

        class PaginatedResponse(BaseModel):
            items: List[Dict]
            pagination: Dict[str, int]

        @paginate(PaginatedResponse)
        def get_items():
            return [{"id": i} for i in range(1, 101)]
        ```
        Call the endpoint with query parameters `?page=2&limit=10` to get
        the second page of 10 items.

    Notes:
        - The decorated function should return a list of items.
        - The `response_model` should have two fields:
          - `items` for the sliced list of items.
          - `pagination` for metadata including total items, total pages,
            current page, and limit.
    """

    def decorator(func):
        """ doc """
        @wraps(func)
        async def wrapper(*args, page: int = 1, limit: int = 10, **kwargs):
            """ doc """
            # Validate the limit and page
            if page < 1 or limit < 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Page and limit must be greater than 0."
                )

            # Call the original function to get the full list of items
            items = await func(*args, **kwargs)

            if not isinstance(items, list):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="The decorated function must return a list."
                )

            # Calculate pagination details
            total_items = len(items)
            total_pages = ceil(total_items / limit)
            if page > total_pages:
                page = total_pages

            # Get the slice of items for the current page
            start = (page - 1) * limit
            end = start + limit
            paginated_items = items[start:end]

            # Prepare pagination info
            pagination_info = {
                "total": total_items,
                "totalPages": total_pages,
                "currentPage": page,
                "limit": limit,
            }

            # Return response model with paginated items and pagination info
            return response_model(items=paginated_items, pagination=pagination_info)

        return wrapper
    return decorator
