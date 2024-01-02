import laspy

def cropping_lazfile(input_filename, output_filename, x_center, y_center, box_size):
    # Open the LAZ file
    input_file = laspy.read(input_filename)

    min_x = x_center - (box_size / 2)
    max_x = x_center + (box_size / 2)
    min_y = y_center - (box_size / 2)
    max_y = y_center + (box_size / 2)

    # Create a mask that selects points within the boundary
    mask = (input_file.x >= min_x) & (input_file.x <= max_x) & \
           (input_file.y >= min_y) & (input_file.y <= max_y)

    # Apply the mask to get the cropped points
    cropped_points = input_file[mask]

    # Create a new LAS object for the output
    output_file = laspy.create(point_format=input_file.header.point_format,
                               file_version=input_file.header.version)

    # Set the points and header data
    output_file.points = cropped_points.points
    output_file.header = cropped_points.header

    # Write to a new LAZ file
    output_file.write(output_filename)

# Example Usage
cropping_lazfile("69BZ2_19.LAZ", "output_cropped_file.laz", 188299, 314370, 500)
