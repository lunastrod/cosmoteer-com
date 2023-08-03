import part_data
import cosmoteer_save_tools
GRAPHICS=1
if(GRAPHICS==1):
    import cv2
    import numpy as np


def add_mass_to_parts(parts_list):
    for part in parts_list:
        part_id = part["ID"]
        part["mass"] = part_data.parts[part_id]["mass"]
        
    return parts_list

def center_of_mass(parts):
    total_mass = 0
    sum_x_mass = 0
    sum_y_mass = 0

    for part in parts:
        mass=part["mass"]
        x_coord=part["Location"][0]
        y_coord=part["Location"][1]

        total_mass += mass
        sum_x_mass += mass * x_coord
        sum_y_mass += mass * y_coord


    if total_mass == 0:
        center_of_mass_x = 0
        center_of_mass_y = 0
    else:
        center_of_mass_x = sum_x_mass / total_mass
        center_of_mass_y = sum_y_mass / total_mass

    return center_of_mass_x, center_of_mass_y

def add_parts_to_tiles(tiles, parts, com):
    for part in parts:
        x_coord = part["Location"][0] +60
        y_coord = part["Location"][1] +60
        if(part["ID"] == "cosmoteer.armor" or part["ID"]=="cosmoteer.armor_2x1"):
            tiles[y_coord][x_coord] = "X"
        else:
            tiles[y_coord][x_coord] = "."
        tiles[round(com[1])+60][round(com[0])+60] = "O"

def print_tiles(tiles):
    for i in range(120):
        for j in range(120):
            print(tiles[i][j], end="")
        print()

def draw_ship(parts, com):
    if(GRAPHICS==1):
        cvdraw_ship(parts, com)
    else:
        tiles = [[" " for i in range(120)] for j in range(120)]
        add_parts_to_tiles(tiles, parts, com)
        print_tiles(tiles)

def cvdraw_ship(parts, com):
    #use opencv to draw ship
    print("drawing ship")
    #create blank image factor times of the ship
    size_factor = 8
    square_size = round(size_factor/2.5)
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
        cv2.rectangle(img, (x_coord*size_factor-square_size, y_coord*size_factor-square_size),
                           (x_coord*size_factor+square_size, y_coord*size_factor+square_size),
                           color, -1)
    #add center of mass (as a green circle)

    #cv2.rectangle(img, (round(com[0]+60)*size_factor-square_size, round(com[1]+60)*size_factor-square_size),
    #                   (round(com[0]+60)*size_factor+square_size, round(com[1]+60)*size_factor+square_size),
    #                   [0,255,0], -1)
    cv2.circle(img, (round((com[0]+60)*size_factor), round((com[1]+60)*size_factor)), square_size*2, [0,255,0], -1)

    #show image
    cv2.imshow("image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if(__name__ == "__main__"):
    #read ship.png, extract part data
    ship="ships/The_Blue_Pages.ship.png"
    parts=cosmoteer_save_tools.Ship(ship).data["Parts"]
    #add mass data to parts
    parts=add_mass_to_parts(parts)
    #calculate center of mass
    com = center_of_mass(parts)
    #draw ship
    draw_ship(parts, com)
