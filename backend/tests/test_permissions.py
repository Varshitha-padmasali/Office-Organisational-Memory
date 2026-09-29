"""
Tests for role/permission enforcement on protected routes.

STATUS (Day 1): there is no auth or role model wired to any route yet
(see app/api/dependencies.get_current_user, which currently always raises
501). This file is explicitly skipped rather than faked so `pytest`
output honestly reflects what's built.
"""

import pytest

pytestmark = pytest.mark.skip(
    reason="Auth/permissions not implemented yet — planned for Day 2."
)


def test_unauthenticated_request_is_rejected():
    ...


def test_user_cannot_access_another_users_documents():
    ...
