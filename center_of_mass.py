# Copyright 2023 LunastroD

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use,  
# copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software
# is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF 
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE 
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION 
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# INSTRUCTIONS:
# move your ship.png to the ships folder
# change the SHIP variable to the name of your ship.png
# if you have opencv installed, set GRAPHICS to 1 to draw your ship
#   the center of mass of your ship will be drawn as a green circle
#   if you can't see the window, the image will be saved as out.png
# otherwise, set GRAPHICS to 0 to use an ascii representation of your ship
#   the center of mass of your ship will be drawn as an "O"

import part_data
import cosmoteer_save_tools
GRAPHICS=1 #set to 1 to use opencv to draw ship, 0 to use ascii representation
DRAW_ALL_COM=0
DRAW_ALL_COT=1
WINDOWED=0 #set to 1 to show the opencv window
SHIP="ships/Nion.ship.png" #set to the name of your ship.png
if(GRAPHICS==1):
    import cv2
    import numpy as np

def part_mass(part):
    return part_data.parts[part["ID"]]["mass"]

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

def part_center_of_thrust(part):
    #each part has a center of thrust, relative to its own origin
    #use part_data.thruster_data[part["ID"]][cot] to get the center of thrust relative to the origin
    #the origin is the top left corner
    #some parts don't have a center of thrust, we return 0 for those

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

def center_of_mass(parts):
    total_mass = 0
    sum_x_mass = 0
    sum_y_mass = 0

    for part in parts:
        mass=part_mass(part)
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
                mass=part_mass(part)
                x_coord=cot[0]
                y_coord=cot[1]

                total_thrust += mass
                sum_x_thrust += mass * x_coord
                sum_y_thrust += mass * y_coord

    if(total_thrust == 0):
        return 0
    return sum_x_thrust / total_thrust, sum_y_thrust / total_thrust



def ascii_draw(tiles, parts, com):
    for part in parts:
        x_coord = part["Location"][0] +60
        y_coord = part["Location"][1] +60
        size=part_data.parts[part["ID"]]["size"]
        rotation=part["Rotation"]
        if(rotation==1 or rotation==3):
            size=(size[1],size[0])
        for i in range(size[0]):
            for j in range(size[1]):
                if(part["ID"] in ["cosmoteer.armor", "cosmoteer.armor_2x1","cosmoteer.armor_wedge","cosmoteer.armor_1x2_wedge","cosmoteer.armor_1x3_wedge","cosmoteer.armor_tri","cosmoteer.armor_structure_hybrid_1x1","cosmoteer.armor_structure_hybrid_1x2","cosmoteer.armor_structure_hybrid_1x3","cosmoteer.armor_structure_hybrid_tri"]):
                    tiles[y_coord+j][x_coord+i] = "X"
                else:
                    tiles[y_coord+j][x_coord+i] = "."
        tiles[round(com[1])+60][round(com[0])+60] = "O"

def print_tiles(tiles):
    for i in range(120):
        for j in range(120):
            print(tiles[i][j], end="")
        print()

def draw_ship(parts, com, output_filename):
    if(GRAPHICS==1):
        print("center of mass: ", com)
        cvdraw_ship(parts, com, output_filename)
    else:
        tiles = [[" " for i in range(120)] for j in range(120)]
        ascii_draw(tiles, parts, com)
        print_tiles(tiles)
        print("center of mass: ", com)

def cvdraw_ship(parts, com, output_filename):
    #use opencv to draw ship
    #create blank image factor times of the ship
    size_factor = 8
    square_size = round(size_factor)
    img = np.zeros((120*size_factor,120*size_factor,3), np.uint8)

    #add parts to image
    for part in parts:
        x_coord = part["Location"][0] +60
        y_coord = part["Location"][1] +60
        if(part["ID"] in ["cosmoteer.shield_gen_small","cosmoteer.shield_gen_large","cosmoteer.control_room_small","cosmoteer.control_room_med","cosmoteer.control_room_large", "cosmoteer.armor", "cosmoteer.armor_2x1","cosmoteer.armor_wedge","cosmoteer.armor_1x2_wedge","cosmoteer.armor_1x3_wedge","cosmoteer.armor_tri","cosmoteer.armor_structure_hybrid_1x1","cosmoteer.armor_structure_hybrid_1x2","cosmoteer.armor_structure_hybrid_1x3","cosmoteer.armor_structure_hybrid_tri"]):
            color = [125,0,0]#armor shields and control rooms are blue
        elif(part["ID"] in ["cosmoteer.structure","cosmoteer.structure_wedge","cosmoteer.structure_1x2_wedge","cosmoteer.structure_1x3_wedge","cosmoteer.structure_tri","cosmoteer.corridor","cosmoteer.fire_extinguisher","cosmoteer.airlock","cosmoteer.crew_quarters_small","cosmoteer.crew_quarters_med","cosmoteer.conveyor","cosmoteer.storage_2x2","cosmoteer.storage_3x2","cosmoteer.storage_3x3","cosmoteer.storage_4x3","cosmoteer.storage_4x4"]):
            color = [125,125,125]#structure and hull is grey
        elif(part["ID"] in ["cosmoteer.power_storage","cosmoteer.thruster_small","cosmoteer.thruster_med","cosmoteer.thruster_large","cosmoteer.thruster_small_2way","cosmoteer.thruster_small_3way","cosmoteer.thruster_huge","cosmoteer.thruster_boost","cosmoteer.engine_room","cosmoteer.reactor_small","cosmoteer.reactor_med","cosmoteer.reactor_large"]):
            color = [0, 125, 125]#thrusters and reactors are yellow
        elif(part["ID"] in ["cosmoteer.laser_blaster_small","cosmoteer.laser_blaster_large","cosmoteer.disruptor","cosmoteer.ion_beam_emitter","cosmoteer.ion_beam_prism","cosmoteer.tractor_beam_emitter","cosmoteer.point_defense","cosmoteer.mining_laser_small","cosmoteer.cannon_med","cosmoteer.cannon_large","cosmoteer.cannon_deck","cosmoteer.explosive_charge","cosmoteer.missile_launcher","cosmoteer.railgun_loader","cosmoteer.railgun_accelerator","cosmoteer.railgun_launcher","cosmoteer.flak_cannon_large"]):
            color=[0,0,125]#weapons are red
        else:
            color = [125,0,125]#everything else is purple
        size=part_data.parts[part["ID"]]["size"]
        rotation=part["Rotation"]
        if(rotation==1 or rotation==3):
            size=(size[1],size[0])
            
        for i in range(size[0]):
            for j in range(size[1]):
                cv2.rectangle(img, (round((x_coord+i)*size_factor+1), round((y_coord+j)*size_factor+1)),
                                (round((x_coord+i+1)*size_factor-1), round((y_coord+j+1)*size_factor-1)),
                                color, -1)
                
    #add center of mass (as a green circle)
    cv2.circle(img, (round((com[0]+60)*size_factor), round((com[1]+60)*size_factor)), square_size, [0,255,0], -1)
    if(DRAW_ALL_COM):
        #add center of mass of each part (as a green circle)
        for part in parts:
            x_coord,y_coord=part_center_of_mass(part)
            cv2.circle(img, (round((x_coord+60)*size_factor), round((y_coord+60)*size_factor)), 1, [0,255,0], -1)

    if(DRAW_ALL_COT):
        #add center of thrust of each part (as a red circle)
        for part in parts:
            cots=part_center_of_thrust(part)
            if(cots==0):
                continue
            for cot in cots:
                #cv2.circle(img, (round((cot[0]+60)*size_factor), round((cot[1]+60)*size_factor)), 1, [0,0,255], -1)
                part_rotation = cot[2]
                end_point = (0,0)
                if(part_rotation==0):
                    end_point = (cot[0], cot[1]-2)
                elif(part_rotation==1):
                    end_point = (cot[0]+2, cot[1])
                elif(part_rotation==2):
                    end_point = (cot[0], cot[1]+2)
                elif(part_rotation==3):
                    end_point = (cot[0]-2, cot[1])

                #instead of drawing a line, draw an arrow
                cv2.arrowedLine(img, (round((cot[0]+60)*size_factor), round((cot[1]+60)*size_factor)), (round((end_point[0]+60)*size_factor), round((end_point[1]+60)*size_factor)), [0,0,255], 2, tipLength=0.3)
    
    #draw center of thrust of the ship (as a red arrow)
    cot = center_of_thrust(parts, 0)
    if(cot!=0):
        end_point = (cot[0], cot[1]-10)
        cv2.arrowedLine(img, (round((cot[0]+60)*size_factor), round((cot[1]+60)*size_factor)), (round((end_point[0]+60)*size_factor), round((end_point[1]+60)*size_factor)), [0,127,255], 3, tipLength=0.3)

    #save image
    cv2.imwrite(output_filename, img)
    #show image
    if(WINDOWED):
        cv2.imshow("image", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def com(input_filename, output_filename):
    #read ship.png, extract part data
    parts=cosmoteer_save_tools.Ship(input_filename).data["Parts"]
    #calculate center of mass
    com = center_of_mass(parts)
    #draw ship
    draw_ship(parts, com, output_filename)#writes to out.png
    return com

if(__name__ == "__main__"):
    com(SHIP, "out.png")


