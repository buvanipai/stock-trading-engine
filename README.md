# stock-trading-engine

# Real-Time Stock Trading Engine

## Project Overview
This project implements a high-performance stock trading engine that matches buy and sell orders across multiple stock tickers. The system handles concurrent order submissions while maintaining data consistency and meeting performance requirements.

## Key Features
- Support for 1,024 different stock tickers
- Thread-safe order processing
- O(n) time complexity for order matching
- Custom linked list implementation without using dictionaries/maps
- Simulation capability to test system performance

## Implementation Approach

### Data Structure Choice
I chose linked lists to store and organize orders because:
- They satisfy the "no dictionaries/maps" requirement
- They allow for efficient sorting of orders by price
- They enable the O(n) matching algorithm required by the specification
- They're straightforward to implement from scratch

### Order Matching
The matching process follows a simple principle:
1. Compare the highest buy order with the lowest sell order
2. If buy price ≥ sell price, execute a trade at the seller's price
3. Update quantities and continue matching until no more matches are possible

### Concurrency Handling
To handle multiple threads submitting orders simultaneously:
- Each ticker has its own order book to reduce contention
- The implementation uses separate locks for buy and sell orders
- Lock ordering prevents deadlocks

## Design Decisions
- Orders are sorted during insertion to speed up matching
- Inactive orders are marked rather than removed
- The system balances simplicity with performance

## Potential Enhancements
With more time, the system could be extended to support:
- Order cancellation functionality
- Different order types (market, limit, stop, etc.)
- More comprehensive logging and reporting

## Testing
The included simulation tests the system under load with multiple threads generating random orders, demonstrating the engine's ability to handle concurrent operations correctly.
