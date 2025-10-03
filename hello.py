from datetime import datetime, timedelta

def add_numbers(a, b):
    """
    Function to add two numbers
    
    Args:
        a: First number
        b: Second number
    
    Returns:
        Sum of a and b
    """
    return a + b


def print_stock_data(stock_data):
    """
    Function to print stock data points

    Args:
        stock_data: List of dictionaries containing 'time' and 'price' keys
    """
    print("Stock Data Points:")
    print("-" * 40)
    for i, data_point in enumerate(stock_data, 1):
        time = data_point['time']
        price = data_point['price']
        print(f"{i:2d}. {time.strftime('%A %H:%M')} - ${price:.2f}")


def generate_sample_stock_data():
    """
    Generate sample stock data for Monday to Friday, 8 hours per day (40 total points)
    
    Returns:
        List of stock data points with time and price
    """ 
    stock_data = []
    base_price = 100.0
    
    # Start from Monday 9 AM
    start_date = datetime(2025, 9, 29, 9, 0)  # Monday
    
    for day in range(5):  # Monday to Friday
        for hour in range(8):  # 8 hours per day (9 AM to 5 PM)
            current_time = start_date + timedelta(days=day, hours=hour)
            # Simulate price fluctuation
            price_change = (hour - 4) * 0.5 + day * 2.0
            current_price = base_price + price_change
            
            stock_data.append({
                'time': current_time,
                'price': current_price
            })
    
    return stock_data


#print(f"Adding 10 + 7 = {add_numbers(10, 7)}")

# Generate and print sample stock data
sample_data = generate_sample_stock_data()
print_stock_data(sample_data)