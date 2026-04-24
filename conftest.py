import pytest
from django.db import connection


@pytest.fixture(autouse=True)
def reset_database():
    """Reset database state before each test."""
    with connection.cursor() as cursor:
        # Disable foreign key checks
        cursor.execute("PRAGMA foreign_keys=OFF")

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        # Delete from all tables except sqlite internal ones
        for table in tables:
            if not table.startswith('sqlite_'):
                try:
                    cursor.execute(f"DELETE FROM {table}")
                except Exception:
                    pass

        # Re-enable foreign key checks
        cursor.execute("PRAGMA foreign_keys=ON")

    yield