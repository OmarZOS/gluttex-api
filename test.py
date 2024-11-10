import httpx
import asyncio
from typing import List
import random

BASE_URL = "http://localhost:8000/business/order/add"

# Sample Data for Testing
sample_ordered_item = {
    "id_ordered_item": None,
    "ordered_product_id": 1,
    "ordering_user_id": 1,
    "order_ref": 12345,
    "product_discount": 10,
    "ordered_quantity": 5,
    "unit_price": 100,
    "applied_vat": 12
}

sample_placed_order = {
    "id_placed_order": None,
    "ordered_timestamp": "2024-10-30T10:00:00",
    "order_discount": "5"
}

# Basic request function
async def send_request(client, ordered_items, placed_order):
    response = await client.put(
        BASE_URL,
        json={"ordered_items": ordered_items, "submitted_order": placed_order}
    )
    return response.json()

# High Traffic Test: Send multiple requests simultaneously
async def high_traffic_test():
    async with httpx.AsyncClient() as client:
        tasks = []
        for _ in range(100):  # Adjust the count for load level
            ordered_items = [sample_ordered_item] * random.randint(1, 5)
            placed_order = sample_placed_order
            tasks.append(send_request(client, ordered_items, placed_order))
        results = await asyncio.gather(*tasks)
        for result in results:
            print(result)

# Large Payload Test: Send a request with a large list of items
async def large_payload_test():
    async with httpx.AsyncClient() as client:
        ordered_items = [sample_ordered_item] * 1000  # Large payload
        placed_order = sample_placed_order
        result = await send_request(client, ordered_items, placed_order)
        print("Large Payload Test Result:", result)

# Race Condition Test: Rapid, simultaneous submissions for the same order
async def race_condition_test():
    async with httpx.AsyncClient() as client:
        tasks = []
        ordered_items = [sample_ordered_item] * 5
        placed_order = sample_placed_order
        for _ in range(50):  # Rapid concurrent requests
            tasks.append(send_request(client, ordered_items, placed_order))
        results = await asyncio.gather(*tasks)
        for result in results:
            print(result)

# Run tests
async def main():
    print("Basic Request Test:")
    await send_request(httpx.AsyncClient(), [sample_ordered_item], sample_placed_order)
    
    print("\nHigh Traffic Test:")
    await high_traffic_test()
    
    print("\nLarge Payload Test:")
    await large_payload_test()
    
    print("\nRace Condition Test:")
    await race_condition_test()

asyncio.run(main())
