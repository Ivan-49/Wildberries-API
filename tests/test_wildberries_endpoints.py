import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from loguru import logger
