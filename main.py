import threading
import random
import time
from enum import Enum
from typing import List, Tuple, Optional

# Constants
MAX_TICKETS = 1024
MAX_ORDERS = 10000

# Order Tyoes
class OrderType(Enum):
    BUY = 0
    SELL = 1

# Order class
class Order:
    def __init__(self, order_type: OrderType, ticker_index: int, quantity: int, price: float):
        self.type = order_type
        self.ticker_index = ticker_index
        self.quantity = quantity
        self.price = price
        self.active = True
        
# Node for our custom linked list
class OrderNode:
    def __init__(self, order: Order):
        self.order = order
        self.next = None
        
# Order book for each ticker
class OrderBook:
    def __init__(self):
        self.buy_head = None # Head of buy orders list
        self.sell_head = None # Head of sell orders list
        self.buy_lock = threading.Lock()
        self.sell_lock = threading.Lock()
        
    # Add a buy order
    def add_buy_order(self, order:Order):
        new_node = OrderNode(order)
        
        with self.buy_lock:
            # Insert into the buy list (sorted by price in descending order)
            if self.buy_head is None or self.buy_head.order.price < order.price:
                new_node.next = self.buy_head
                self.buy_head = new_node
            else:
                curr = self.buy_head
                prev = None
                
                while curr is not None and curr.order.price >= order.price:
                    prev = curr
                    curr = curr.next
                    
                new_node.next = curr
                prev.next = new_node
                
    def add_sell_order(self, order: Order):
        new_node = OrderNode(order)
        
        with self.sell_lock:
            if self.sell_head is None or self.sell_head.order.price > order.price:
                new_node.next = self.sell_head
                self.sell_head = new_node
            else:
                curr = self.sell_head
                prev = None
                
                while curr is not None and curr.order.price <= order.price:
                    prev = curr
                    curr = curr.next
                    
                new_node.next = curr
                prev.next = new_node
                
    def get_best_buy_price(self) -> Tuple[bool, float]:
        with self.buy_lock:
            curr = self.buy_head
            
            while curr is not None:
                if curr.order.active:
                    return True, curr.order.price
                curr = curr.next
                
            return False, 0.0
        
    def get_best_sell_price(self) -> Tuple[bool, float]:
        with self.sell_lock:
            curr = self.sell_head
            
            while curr is not None:
                if curr.order.active:
                    return True, curr.order.price
                curr = curr.next
                
            return False, 0.0
        
    def match_orders(self):
        # Use a compound lock to prevent deadlocks
        with self.buy_lock, self.sell_lock:
            buy = self.buy_head
            sell = self.sell_head
            
            while buy is not None and sell is not None:
                # skip inactive orders
                if not buy.order.active:
                    buy = buy.next
                    continue
                
                if not sell.order.active:
                    sell = sell.next
                    continue
                
                # Check if the orders match
                if buy.order.price >= sell.order.price:
                    # Match found! Execute the trade
                    trade_qty = min(buy.order.quantity, sell.order.quantity)
                    trade_price = sell.order.price # Use the seller's price
                    
                    # Update quantities
                    buy.order.quantity -= trade_qty
                    sell.order.quantity -= trade_qty
                    
                    # Print the trade
                    print(f"TRADE: Ticker {buy.order.ticker_index} | Quantity: {trade_qty} | Price: {trade_price:.2f}")
                    
                    # Mark orders as inactive if fully filled
                    if buy.order.quantity <= 0:
                        buy.order.active = False
                        buy = buy.next
                        
                    if sell.order.quantity <= 0:
                        sell.order.active = False
                        sell = sell.next
                        
                else:
                    # No match possible, exit
                    break
                
    # global array of books, one for each ticker
order_books = [OrderBook() for _ in range(MAX_TICKETS)]

def add_order(order_type: OrderType, ticker_index: int, quantity: int, price: float):
    if ticker_index < 0 or ticker_index >= MAX_TICKETS:
        print("Invalid ticker index")
        return
    
    order = Order(order_type, ticker_index, quantity, price)
    
    if order_type == OrderType.BUY:
        order_books[ticker_index].add_buy_order(order)
    else:
        order_books[ticker_index].add_sell_order(order)
        
    # After adding an order, try to match orders for this ticker
    order_books[ticker_index].match_orders()

# Wrapper function to randomly generate orders 
def generate_random_orders(num_orders: int):
    for i in range(num_orders):
        order_type = OrderType(random.randint(0, 1))
        ticker = random.randint(0, MAX_TICKETS - 1)
        quantity = random.randint(1, 100)
        price = round(random.uniform(10.0, 1000.0), 2)
        
        add_order(order_type, ticker, quantity, price)
        
        # Sleep a short random time to simulate real-world timing
        time.sleep(0.001)

# Function to match orders across all tickers
def match_all_order():
    for i in range(MAX_TICKETS):
        order_books[i].match_orders()
        
# Simulate trading with multiple threads
def run_simulation():
    NUM_THREADS = 4
    ORDERS_PER_THREAD = 250
    
    threads = []
    
    for i in range(NUM_THREADS):
        thread = threading.Thread(target=generate_random_orders, args=(ORDERS_PER_THREAD,))
        threads.append(thread)
        thread.start()
        
    for thread in threads:
        thread.join()
        
    # Final matching sweep
    match_all_order()
    print("Simulation complete.")
    
if __name__ == "__main__":
    run_simulation()