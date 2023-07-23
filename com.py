def center_of_mass(arr):
    total_mass = 0
    x_weighted_sum = 0
    y_weighted_sum = 0

    rows = len(arr)
    cols = len(arr[0])

    for i in range(rows):
        for j in range(cols):
            mass = arr[i][j]
            total_mass += mass
            x_weighted_sum += j * mass
            y_weighted_sum += i * mass

    center_x = x_weighted_sum / total_mass
    center_y = y_weighted_sum / total_mass

    return center_x, center_y

# Example usage:
bidimensional_array = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

center_x, center_y = center_of_mass(bidimensional_array)
print("Center of Mass: (x={}, y={})".format(center_x, center_y))
