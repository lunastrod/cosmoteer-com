import part_data

def part_center_of_mass(part):
    #each part has a center of mass, relative to its own origin
    #a decent approximation is to use the center of the tiles of the part
    #parts have a size parameter, the origin is the top left corner

    #get part size
    part_size = part_data.parts[part["ID"]]["size"]
    part_rotation = part["Rotation"]#0,1,2,3
    #calculate center of mass
    if(part_rotation==0 or part_rotation==2):
        center_of_mass_x = part["Location"][0] + part_size[0]/2
        center_of_mass_y = part["Location"][1] + part_size[1]/2
    elif(part_rotation==1 or part_rotation==3):
        center_of_mass_x = part["Location"][0] + part_size[1]/2
        center_of_mass_y = part["Location"][1] + part_size[0]/2
    else:
        print("ERROR: part_rotation not 0,1,2,3")
    return center_of_mass_x, center_of_mass_y

def center_of_mass(parts):
    total_mass = 0
    sum_x_mass = 0
    sum_y_mass = 0

    for part in parts:
        mass=part_data.parts[part["ID"]]["mass"]
        x_coord,y_coord=part_center_of_mass(part)

        total_mass += mass
        sum_x_mass += mass * x_coord
        sum_y_mass += mass * y_coord


    if total_mass == 0:
        center_of_mass_x = 0
        center_of_mass_y = 0
    else:
        center_of_mass_x = sum_x_mass / total_mass
        center_of_mass_y = sum_y_mass / total_mass

    return center_of_mass_x, center_of_mass_y, total_mass
