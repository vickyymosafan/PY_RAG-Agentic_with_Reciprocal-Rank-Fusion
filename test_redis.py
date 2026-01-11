"""Test Redis Cache Service."""
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

from app.infrastructure.cache.redis_cache import RedisCacheService


async def test_redis():
    """Test Redis health check dan basic operations."""
    print("=" * 50)
    print("Testing Redis Cache Service")
    print("=" * 50)
    
    svc = RedisCacheService()
    
    # Test 1: Health Check
    print("\n[1] Testing Health Check...")
    result = await svc.health_check()
    print(f"    Status: {result['status']}")
    print(f"    Connected: {result['connected']}")
    print(f"    Latency: {result['latency_ms']} ms")
    if result['error']:
        print(f"    Error: {result['error']}")
    
    # Test 2: Set/Get
    print("\n[2] Testing Set/Get...")
    set_result = await svc.set("test_key", {"message": "Hello from test!"}, ttl=60)
    print(f"    Set result: {set_result}")
    
    get_result = await svc.get("test_key")
    print(f"    Get result: {get_result}")
    
    # Test 3: Delete
    print("\n[3] Testing Delete...")
    del_result = await svc.delete("test_key")
    print(f"    Delete result: {del_result}")
    
    exists_after = await svc.exists("test_key")
    print(f"    Exists after delete: {exists_after}")
    
    # Cleanup
    await svc.close()
    print("\n" + "=" * 50)
    print("Test completed!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_redis())
