import os
import sys
import asyncio
import importlib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_package(name):
    try:
        mod = importlib.import_module(name)
        version = getattr(mod, "__version__", "unknown")
        print(f"[OK] {name} (Version: {version})")
        return True
    except ImportError as e:
        print(f"[FAILED] {name} is not installed: {e}")
        return False

async def check_postgres():
    try:
        import asyncpg
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            print("[FAILED] DATABASE_URL not found in .env")
            return False
            
        # Convert SQLAlchemy asyncpg URL to standard PostgreSQL URL for asyncpg
        if db_url.startswith("postgresql+asyncpg://"):
            db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
            
        conn = await asyncpg.connect(db_url)
        await conn.close()
        print("[OK] PostgreSQL Connection")
        return True
    except Exception as e:
        print(f"[FAILED] PostgreSQL connection: {e}")
        return False

async def main():
    print("=" * 40)
    print("SYSTEM ENVIRONMENT AUDIT & CHECK")
    print("=" * 40)
    
    # Python Version Check
    print(f"[OK] Python {sys.version}")
    
    # Packages check
    packages_ok = True
    for pkg in ["torch", "torchvision", "fastapi", "uvicorn", "tenseal", "opacus", "flwr", "jwt", "passlib", "bcrypt"]:
        if not check_package(pkg):
            packages_ok = False
            
    # PostgreSQL check
    pg_ok = await check_postgres()
    
    print("=" * 40)
    if packages_ok and pg_ok:
        print("ALL TESTS PASSED: ENVIRONMENT STATUS [OK]")
        sys.exit(0)
    else:
        print("SOME TESTS FAILED: ENVIRONMENT STATUS [ERROR]")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
