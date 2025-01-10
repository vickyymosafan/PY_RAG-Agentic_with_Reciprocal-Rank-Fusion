"""Test PostgreSQL Database Connection."""
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

from app.infrastructure.database.connection import health_check, init_db, close_db, get_db_session
from sqlalchemy import text


async def test_postgresql():
    """Test PostgreSQL health check dan basic operations."""
    print("=" * 50)
    print("Testing PostgreSQL Database Connection")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n[1] Testing Health Check...")
    result = await health_check()
    print(f"    Status: {result['status']}")
    print(f"    Connected: {result['connected']}")
    print(f"    Latency: {result['latency_ms']} ms")
    if result['error']:
        print(f"    Error: {result['error']}")
        print("\n❌ Database connection FAILED!")
        print("\nPastikan:")
        print("  1. PostgreSQL service berjalan")
        print("  2. Database 'rag_db' sudah dibuat")
        print("  3. Password di .env sesuai (Admin)")
        await close_db()
        return
    
    # Test 2: Init DB (create tables)
    print("\n[2] Initializing Database Tables...")
    try:
        await init_db()
        print("    Tables initialized successfully")
    except Exception as e:
        print(f"    Error: {e}")
    
    # Test 3: Simple Query
    print("\n[3] Testing Simple Query...")
    try:
        async with get_db_session() as session:
            result = await session.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"    PostgreSQL Version: {version[:50]}...")
    except Exception as e:
        print(f"    Error: {e}")
    
    # Cleanup
    await close_db()
    print("\n" + "=" * 50)
    print("Test completed!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_postgresql())
