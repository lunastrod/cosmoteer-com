import part_data

def part_center_of_thrust(part):
    #each part has a center of thrust, relative to its own origin
    #use part_data.thruster_data[part["ID"]][cot] to get the center of thrust relative to the origin
    #the origin is the top left corner
    #some parts don't have a center of thrust, we return 0 for those
    #returns a list of vectors, each vector is (x0,y0,orientation)

    #get part cot
    part_cots = part_data.thruster_data.get(part["ID"], {"cot":0})["cot"]
    if(part_cots==0):
        return 0

    #some parts have multiple cots, we return a list of all of them

    part_rotation = part["Rotation"]#0,1,2,3
    part_size = part_data.parts[part["ID"]]["size"]
    absolute_cots = []
    for part_cot in part_cots:
        #calculate orientation
        orientation = (part_rotation+part_cot[2])%4
        #calculate center of thrust
        if(part_rotation==0):
            center_of_thrust_x = part["Location"][0] + part_cot[0]
            center_of_thrust_y = part["Location"][1] + part_cot[1]
        elif(part_rotation==1):
            center_of_thrust_x = part["Location"][0] - part_cot[1] + part_size[1]
            center_of_thrust_y = part["Location"][1] + part_cot[0]
        elif(part_rotation==2):
            center_of_thrust_x = part["Location"][0] - part_cot[0] + part_size[0]
            center_of_thrust_y = part["Location"][1] - part_cot[1] + part_size[1]
        elif(part_rotation==3):
            center_of_thrust_x = part["Location"][0] + part_cot[1]
            center_of_thrust_y = part["Location"][1] - part_cot[0] + part_size[0]
        else:
            print("ERROR: part_rotation not 0,1,2,3")
        absolute_cots.append((center_of_thrust_x, center_of_thrust_y, orientation))
    return absolute_cots

def center_of_thrust(parts, direction):
    #calculate center of thrust
    #each part has a center of thrust, calculated by part_center_of_thrust(part)
    #the center of thrust of the ship is the weighted average of the centers of thrust of the parts
    #we only consider the thrusters in one direction (direction parameter)
    #returns 0 if there are no thrusters in that direction

    total_thrust = 0
    sum_x_thrust = 0
    sum_y_thrust = 0

    for part in parts:
        cots=part_center_of_thrust(part)
        if(cots==0):
            continue
        for cot in cots:
            if(cot[2]==direction):
                mass=part_data.parts[part["ID"]]["mass"]
                x_coord=cot[0]
                y_coord=cot[1]

                total_thrust += mass
                sum_x_thrust += mass * x_coord
                sum_y_thrust += mass * y_coord

    if(total_thrust == 0):
        return 0
    return sum_x_thrust / total_thrust, sum_y_thrust / total_thrust