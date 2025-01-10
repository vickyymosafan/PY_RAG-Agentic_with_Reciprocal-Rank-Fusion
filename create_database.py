"""Create rag_db database and pgvector extension."""
import asyncio
import asyncpg


async def create_database():
    """Create database rag_db if not exists."""
    print("=" * 50)
    print("Creating Database 'rag_db'")
    print("=" * 50)
    
    # Connect to default 'postgres' database
    try:
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='Admin',
            database='postgres'
        )
        print("✅ Connected to PostgreSQL")
        
        # Check if database exists
        result = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = 'rag_db'"
        )
        
        if result:
            print("✅ Database 'rag_db' already exists")
        else:
            # Create database
            await conn.execute('CREATE DATABASE rag_db')
            print("✅ Database 'rag_db' created successfully")
        
        await conn.close()
        
        # Connect to rag_db to create extension
        print("\n[2] Creating pgvector extension...")
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='Admin',
            database='rag_db'
        )
        
        try:
            await conn.execute('CREATE EXTENSION IF NOT EXISTS vector')
            print("✅ pgvector extension created/verified")
        except Exception as e:
            print(f"⚠️ pgvector extension error: {e}")
            print("    (You may need to install pgvector separately)")
        
        await conn.close()
        print("\n" + "=" * 50)
        print("Database setup completed!")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nPastikan:")
        print("  1. PostgreSQL service berjalan")
        print("  2. Password 'Admin' benar")


if __name__ == "__main__":
    asyncio.run(create_database())
