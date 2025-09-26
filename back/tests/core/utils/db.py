"""Test database utilities."""

# Global query counter for performance testing
_query_count = 0


def increment_query_count(sql):
    """Increment the global query counter for testing."""
    global _query_count
    _query_count += 1


def get_query_count():
    """Get the current query count."""
    return _query_count


def reset_query_count():
    """Reset the query counter."""
    global _query_count
    _query_count = 0
