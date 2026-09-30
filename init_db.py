import asyncio
from backend.database import engine, Base
from backend.models import User, BiometricTemplate, AuthLog, FederatedRound

async def init_tables():
    print("Connecting to PostgreSQL and creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[OK] Database tables created successfully:")
    print("  - users")
    print("  - biometric_templates")
    print("  - auth_logs")
    print("  - federated_rounds")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_tables())
