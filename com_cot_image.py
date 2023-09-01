import cv2
import numpy as np
import cosmoteer_save_tools

import center_of_mass
import center_of_thrust
import part_data

DRAW_ALL_COM=0
DRAW_ALL_COT=1
SHIP="ships\-The_Sun_Vanished-_Ver.1.ship.png" #set to the name of your ship.png

def draw_all_cots(img,parts,size_factor=8):
    for part in parts:
        cots=center_of_thrust.part_center_of_thrust(part)
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

def draw_all_parts(img,parts,size_factor=8):
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
                
def print_tiles(tiles):
    for i in range(120):
        for j in range(120):
            print(tiles[i][j], end="")
        print()
                
def draw_all_coms(img,parts,size_factor=8):
    for part in parts:
        x_coord,y_coord=center_of_mass.part_center_of_mass(part)
        cv2.circle(img, (round((x_coord+60)*size_factor), round((y_coord+60)*size_factor)), 1, [0,255,0], -1)

def cvdraw_ship(parts, com, output_filename):
    #use opencv to draw ship
    #create blank image factor times of the ship
    size_factor = 8
    square_size = round(size_factor)
    img = np.zeros((120*size_factor,120*size_factor,3), np.uint8)

    draw_all_parts(img,parts,size_factor)
                
    #add center of mass (as a green circle)
    cv2.circle(img, (round((com[0]+60)*size_factor), round((com[1]+60)*size_factor)), square_size, [0,255,0], -1)
    if(DRAW_ALL_COM):
        draw_all_coms(img,parts,size_factor)

    if(DRAW_ALL_COT):
        draw_all_cots(img,parts,size_factor)
    #draw center of thrust of the ship (as an orange arrow) with a circle at the start
    cot = center_of_thrust.center_of_thrust(parts, 0)
    cv2.circle(img, (round((cot[0]+60)*size_factor), round((cot[1]+60)*size_factor)), square_size, [0,127,255], -1)
    if(cot!=0):
        end_point = (cot[0], cot[1]-10)
        cv2.arrowedLine(img, (round((cot[0]+60)*size_factor), round((cot[1]+60)*size_factor)), (round((end_point[0]+60)*size_factor), round((end_point[1]+60)*size_factor)), [0,127,255], 3, tipLength=0.3)

    #save image
    cv2.imwrite(output_filename, img)
    #show image

    #cv2.imshow("image", img)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

def draw_ship(parts, com, output_filename):
    #print("center of mass: ", com)
    cvdraw_ship(parts, com, output_filename)


"""
#deprecated, use opencv instead
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
"""


def com_cot_image(input_filename, output_filename):
    #read ship.png, extract part data
    data=cosmoteer_save_tools.Ship(input_filename).data
    parts=data["Parts"]
    print("FlightDirection:", data["FlightDirection"])
    """
    FlightDirections:
    012
    7 3
    654
    """
    #calculate center of mass
    com = center_of_mass.center_of_mass(parts)
    #draw ship
    draw_ship(parts, com, output_filename)#writes to out.png
    return com

if __name__ == "__main__":
    com_cot_image(SHIP, "out.png")