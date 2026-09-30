import asyncio
import asyncpg

async def setup():
    try:
        # Connect to default postgres DB using new password 'postgres'
        conn = await asyncpg.connect("postgresql://postgres:postgres@localhost:5432/postgres")
        
        # 1. Create or update user 'user'
        user_exists = await conn.fetchval("SELECT 1 FROM pg_roles WHERE rolname='user'")
        if not user_exists:
            await conn.execute("CREATE USER \"user\" WITH PASSWORD 'pass' SUPERUSER;")
            print("[OK] User 'user' created with password 'pass'")
        else:
            await conn.execute("ALTER USER \"user\" WITH PASSWORD 'pass';")
            print("[OK] Password for user 'user' updated to 'pass'")

        # 2. Create database biometric_db if it does not exist
        db_exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname='biometric_db'")
        if not db_exists:
            await conn.execute("CREATE DATABASE biometric_db OWNER \"user\";")
            print("[OK] Database 'biometric_db' created")
        else:
            print("[OK] Database 'biometric_db' already exists")

        await conn.close()
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    asyncio.run(setup())
