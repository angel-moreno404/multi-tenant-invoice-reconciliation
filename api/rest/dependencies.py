from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db

# This file can be used for shared REST API dependencies
# Currently, we use get_db directly from core.database

