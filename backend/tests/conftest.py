import pytest

# Register anyio plugin so @pytest.mark.anyio works
pytest_plugins = ("anyio",)


@pytest.fixture(scope="session")
def anyio_backend():
    """Use asyncio as the anyio backend for all async tests."""
    return "asyncio"
