"""MariaDB database management API."""

import sys
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

sys.path.insert(0, "/scripts")

router = APIRouter()


class DatabaseCreate(BaseModel):
    """Request body for creating a database."""
    name: str
    charset: str = "utf8mb4"
    collate: str = "utf8mb4_unicode_ci"


class UserCreate(BaseModel):
    """Request body for creating a user."""
    username: str
    password: str = None  # If None, generate random
    host: str = "%"


class UserWithDatabase(BaseModel):
    """Request body for creating user with database and grants."""
    username: str
    database: str
    password: str = None


@router.get("/databases")
async def list_databases(request: Request):
    """List all databases."""
    try:
        from database import DatabaseManager
        db = DatabaseManager()
        databases = db.list_databases()
        return {"databases": databases, "count": len(databases)}
    except ImportError:
        raise HTTPException(status_code=501, detail="Database module not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/databases")
async def create_database(request: Request, data: DatabaseCreate):
    """Create a new database."""
    try:
        from database import DatabaseManager
        db = DatabaseManager()
        result = db.create_database(data.name, data.charset, data.collate)
        return {"success": result, "database": data.name}
    except ImportError:
        raise HTTPException(status_code=501, detail="Database module not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/databases/{name}")
async def drop_database(request: Request, name: str):
    """Drop a database."""
    # Prevent dropping system databases
    protected = ["mysql", "information_schema", "performance_schema", "sys"]
    if name.lower() in protected:
        raise HTTPException(status_code=403, detail=f"Cannot drop system database: {name}")

    try:
        from database import DatabaseManager
        db = DatabaseManager()
        result = db.drop_database(name)
        return {"success": result, "dropped": name}
    except ImportError:
        raise HTTPException(status_code=501, detail="Database module not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users")
async def list_users(request: Request):
    """List all database users."""
    try:
        from database import DatabaseManager
        db = DatabaseManager()
        users = db.list_users()
        return {"users": users, "count": len(users)}
    except ImportError:
        raise HTTPException(status_code=501, detail="Database module not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users")
async def create_user(request: Request, data: UserCreate):
    """Create a new database user."""
    try:
        from database import DatabaseManager
        import secrets

        db = DatabaseManager()
        password = data.password or secrets.token_urlsafe(16)
        result = db.create_user(data.username, password, data.host)
        return {
            "success": result,
            "username": data.username,
            "password": password,  # Return generated password
            "host": data.host,
        }
    except ImportError:
        raise HTTPException(status_code=501, detail="Database module not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/users/{username}")
async def drop_user(request: Request, username: str, host: str = "%"):
    """Drop a database user."""
    # Prevent dropping root
    if username.lower() == "root":
        raise HTTPException(status_code=403, detail="Cannot drop root user")

    try:
        from database import DatabaseManager
        db = DatabaseManager()
        result = db.drop_user(username, host)
        return {"success": result, "dropped": username}
    except ImportError:
        raise HTTPException(status_code=501, detail="Database module not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users/with-database")
async def create_user_with_database(request: Request, data: UserWithDatabase):
    """Create a user with a database and full privileges."""
    try:
        from database import DatabaseManager
        import secrets

        db = DatabaseManager()
        password = data.password or secrets.token_urlsafe(16)

        # Create database
        db.create_database(data.database)

        # Create user
        db.create_user(data.username, password)

        # Grant privileges
        db.grant_all(data.username, data.database)

        return {
            "success": True,
            "username": data.username,
            "password": password,
            "database": data.database,
        }
    except ImportError:
        raise HTTPException(status_code=501, detail="Database module not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
