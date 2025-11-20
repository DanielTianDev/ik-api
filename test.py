def sum_array(numbers):
    """
    Add all integers in an array using a loop
    
    Args:
        numbers: List of integers to sum
        
    Returns:
        int: The sum of all numbers in the array
    """
    total = 0
    for num in numbers:
        total += num
    return total



# Test with different arrays
test_arrays = [
    [1, 2, 3, 4, 5],
    [10, -5, 3, 8],
    [100, 200, 300],
    []  # Empty array
]

for arr in test_arrays:
    result = sum_array(arr)
    print(f"Sum of {arr} = {result}")