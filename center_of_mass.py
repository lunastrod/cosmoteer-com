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
#   the center of mass of your ship will be drawn as a green circle
#   the center of thrust will be drawn as a green arrow and yellow arrows for each direction
#   if you can't see the window, the image will be saved as out.png

import part_data
import cosmoteer_save_tools
from pathlib import Path
from vector2d import Vector2D

GRAPHICS=1 #set to 1 to use opencv to draw ship
DRAW_ALL_COM=0
DRAW_COM=1
DRAW_COTS=1
DRAW_ALL_COT=0
WINDOWED=0 #set to 1 to show the opencv window
SHIP="ships/mo.ship.png" #set to the name of your ship.png
if(GRAPHICS==1):
    import cv2
    import numpy as np

def parts_touching(part1, part2):
    #returns true if part1 and part2 are touching
    #part1 and part2 are touching if any of their tiles are touching
    part1_size = part_data.parts[part1["ID"]]["size"]
    part2_size = part_data.parts[part2["ID"]]["size"]
    part1_location = part1["Location"]#upper left corner
    part2_location = part2["Location"]#upper left corner
    part1_rotation = part1["Rotation"]#0,1,2,3
    part2_rotation = part2["Rotation"]#0,1,2,3

    if(part1_rotation==1 or part1_rotation==3):
        part1_size=(part1_size[1],part1_size[0])
    if(part2_rotation==1 or part2_rotation==3):
        part2_size=(part2_size[1],part2_size[0])

    #generate list of tiles for each part
    part1_tiles = []
    part2_tiles = []
    for i in range(part1_size[0]):
        for j in range(part1_size[1]):
            part1_tiles.append((part1_location[0]+i, part1_location[1]+j))
    for i in range(part2_size[0]):
        for j in range(part2_size[1]):
            part2_tiles.append((part2_location[0]+i, part2_location[1]+j))

    #expand tiles of part 1 to include adjacent tiles (except diagonals)
    for i in range(part1_size[0]):
        for j in range(part1_size[1]):
            part1_tiles.append((part1_location[0]+i+1, part1_location[1]+j))
            part1_tiles.append((part1_location[0]+i-1, part1_location[1]+j))
            part1_tiles.append((part1_location[0]+i, part1_location[1]+j+1))
            part1_tiles.append((part1_location[0]+i, part1_location[1]+j-1))
    
    #check if any of the tiles of part 1 are touching part 2
    for tile in part1_tiles:
        if(tile in part2_tiles):
            return True
    return False
    
def thruster_touching_engine_room(parts,thruster):
    for part in parts:
        if(part["ID"]=="cosmoteer.engine_room" and parts_touching(thruster,part)):
            return True
    return False

def center_of_thrust(parts):
    #returns a list of vectors in each direction (0,1,2,3,4,5,6,7)
    #each vector is a tuple (originx, originy, endx, endy, thrust)    
    origin_thrust=[Vector2D(0,0),Vector2D(0,0),Vector2D(0,0),Vector2D(0,0)]

    thrust_direction=[0,0,0,0]

    for part in parts:
        cots=part_center_of_thrust(part)
        if(cots==0):
            continue
        for cot in cots:
            origin=cot[0]
            orientation=cot[1]
            #print("cot", cot)
            #thrust=part_data.thruster_data[part["ID"]]["thrust"]
            thrust=cot[2]
            if(thruster_touching_engine_room(parts,part)):
                thrust=thrust*1.5

            thrust_direction[orientation] += thrust
            origin_thrust[orientation] += origin*thrust

    for i in range(len(thrust_direction)):
        if(thrust_direction[i]==0):
            continue
        origin_thrust[i]=origin_thrust[i]/thrust_direction[i]
    #calculate the end of the thrust vector
    thrust_vector=[Vector2D(0,0),Vector2D(0,0),Vector2D(0,0),Vector2D(0,0)]
    #0 is up, 1 is right, 2 is down, 3 is left
    thrust_vector[0]=origin_thrust[0]+Vector2D(0,-thrust_direction[0])
    thrust_vector[1]=origin_thrust[1]+Vector2D(thrust_direction[1],0)
    thrust_vector[2]=origin_thrust[2]+Vector2D(0,thrust_direction[2])
    thrust_vector[3]=origin_thrust[3]+Vector2D(-thrust_direction[3],0)

    return origin_thrust,thrust_vector,thrust_direction

    """
    startx = sum_x_cot / total_thrust_direction
    starty = sum_y_cot / total_thrust_direction
    endx = startx+sum_x_thrust
    endy = starty+sum_y_thrust
    
    return startx, starty, endx, endy, total_thrust_direction/total_thrust
    """

def diagonal_center_of_thrust(origin_thrust,thrust_vector,thrust_direction):
    #calculates the center of thrust vectors for the diagonal directions
    #returns a list of vectors in each direction (0,1,2,3,4,5,6,7)

    #0 is up_left, 1 is up_right, 2 is down_right, 3 is down_left
    diagonal_thrust_vector=[Vector2D(0,0),Vector2D(0,0),Vector2D(0,0),Vector2D(0,0)]
    diagonal_thrust_direction=[0,0,0,0]
    diagonal_origin_thrust=[Vector2D(0,0),Vector2D(0,0),Vector2D(0,0),Vector2D(0,0)]
    """
    #up_left
    if(thrust_direction[0]!=0 and thrust_direction[3]!=0):
        diagonal_thrust_direction[0]=(thrust_direction[0]+thrust_direction[3])**0.5
        diagonal_origin_thrust[0]=Vector2D.Lerp(origin_thrust[0],origin_thrust[3],thrust_direction[3]/(thrust_direction[3]+thrust_direction[0]))
        diagonal_thrust_vector[0]=diagonal_origin_thrust[0]+Vector2D(-thrust_direction[3],-thrust_direction[0])

    #up_right
    if(thrust_direction[1]!=0 and thrust_direction[0]!=0):
        diagonal_thrust_direction[1]=(thrust_direction[0]+thrust_direction[1])**0.5
        diagonal_origin_thrust[1]=Vector2D.Lerp(origin_thrust[0],origin_thrust[1],thrust_direction[1]/(thrust_direction[1]+thrust_direction[0]))
        diagonal_thrust_vector[1]=diagonal_origin_thrust[1]+Vector2D(thrust_direction[1],-thrust_direction[0])

    #down_right
    if(thrust_direction[2]!=0 and thrust_direction[1]!=0):
        diagonal_thrust_direction[2]=(thrust_direction[2]+thrust_direction[1])**0.5
        diagonal_origin_thrust[2]=Vector2D.Lerp(origin_thrust[2],origin_thrust[1],thrust_direction[1]/(thrust_direction[2]+thrust_direction[1]))
        diagonal_thrust_vector[2]=diagonal_origin_thrust[2]+Vector2D(thrust_direction[1],thrust_direction[2])

    #down_left
    if(thrust_direction[2]!=0 and thrust_direction[3]!=0):
        diagonal_thrust_direction[3]=(thrust_direction[2]+thrust_direction[3])**0.5
        diagonal_origin_thrust[3]=Vector2D.Lerp(origin_thrust[2],origin_thrust[3],thrust_direction[3]/(thrust_direction[2]+thrust_direction[3]))
        diagonal_thrust_vector[3]=diagonal_origin_thrust[3]+Vector2D(-thrust_direction[3],thrust_direction[2])

    """
    for i in range(4):
        if(thrust_direction[i]!=0 and thrust_direction[(i+3)%4]!=0):
            diagonal_thrust_direction[i]=(thrust_direction[i]**2+thrust_direction[(i+3)%4]**2)**0.5
            print("aaaaaaaaaa")
            print(diagonal_thrust_direction[i])
            diagonal_origin_thrust[i]=Vector2D.Lerp(origin_thrust[i],origin_thrust[(i+3)%4],thrust_direction[(i+3)%4]/(thrust_direction[(i+3)%4]+thrust_direction[i]))
    diagonal_thrust_vector[0]=diagonal_origin_thrust[0]+Vector2D(-thrust_direction[3],-thrust_direction[0])
    diagonal_thrust_vector[1]=diagonal_origin_thrust[1]+Vector2D(thrust_direction[1],-thrust_direction[0])
    diagonal_thrust_vector[2]=diagonal_origin_thrust[2]+Vector2D(thrust_direction[1],thrust_direction[2])
    diagonal_thrust_vector[3]=diagonal_origin_thrust[3]+Vector2D(-thrust_direction[3],thrust_direction[2])

    all_thrust_vector=[]
    all_thrust_direction=[]
    all_origin_thrust=[]
    for i in range(4):
        all_thrust_vector.append(diagonal_thrust_vector[i])
        all_thrust_vector.append(thrust_vector[i])
        all_thrust_direction.append(diagonal_thrust_direction[i])
        all_thrust_direction.append(thrust_direction[i])
        all_origin_thrust.append(diagonal_origin_thrust[i])
        all_origin_thrust.append(origin_thrust[i])
    return all_origin_thrust,all_thrust_vector,all_thrust_direction

def top_speed(mass,thrust):
    """
    speed=0
    for i in range(100):
        drag=(max(speed / 75, 1)**2 * speed * 0.4)
        acceleration=thrust/mass-drag
        speed=speed+acceleration/30
    return speed
    """
    print(thrust)
    correction=1
    x=thrust/mass
    speed=2.5*x*correction
    if(speed>75):
        correction=1
        speed=(14062.5*x)**(1/3)*correction
    return speed

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

    #returns a list of tuples (origin(x,y),orientation,thrust) representing the multiple cots of a part

    #get part cot
    part_cots = part_data.thruster_data.get(part["ID"], {"cot":0})["cot"]
    thrust=part_data.thruster_data.get(part["ID"], {"thrust":0})["thrust"]
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
        absolute_cots.append((Vector2D(center_of_thrust_x,center_of_thrust_y), orientation,thrust))

    for i in range(len(absolute_cots)):
        #each cot has 2 additional cots attatched, they have 5% of the thrust of the main cot on the same origin
        absolute_cots.append((absolute_cots[i][0],(absolute_cots[i][1]+1)%4,absolute_cots[i][2]*0.05))
        absolute_cots.append((absolute_cots[i][0],(absolute_cots[i][1]+3)%4,absolute_cots[i][2]*0.05))
    #print(absolute_cots)
    return absolute_cots

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

def center_of_thrust_vector(parts, ship_direction):
    #calculate the center of thrust vector of the ship in a given direction
    #each part has a center of thrust, calculated by part_center_of_thrust(part)
    #returns a unit vector and the total thrust(originx, originy, endx, endy, thrust) representing the center of thrust vector

    if ship_direction == 0:
        fthruster = [0,3]
    elif ship_direction == 1:
        fthruster = [0]
    elif ship_direction == 2:
        fthruster = [0,1]
    elif ship_direction == 3:
        fthruster = [1]
    elif ship_direction == 4:
        fthruster = [1,2]
    elif ship_direction == 5:
        fthruster = [2]
    elif ship_direction == 6:
        fthruster = [2,3]
    elif ship_direction == 7:
        fthruster = [3]
    
    total_thrust = 0
    total_thrust_direction = 0

    sum_x_cot = 0
    sum_y_cot = 0
    
    sum_x_thrust = 0
    sum_y_thrust = 0

    for part in parts:
        cots=part_center_of_thrust(part)
        if(cots==0):
            continue
        for cot in cots:
            #print("cot", cot)
            thrust=part_data.thruster_data[part["ID"]]["thrust"]
            if(thruster_touching_engine_room(parts,part)):
                thrust=thrust*1.5
            x_coord=cot[0]
            y_coord=cot[1]

            total_thrust += thrust
            if(cot[2] in fthruster):
                total_thrust_direction += thrust

                sum_x_cot += thrust * x_coord
                sum_y_cot += thrust * y_coord
                if(cot[2] == 0):
                    sum_y_thrust -= thrust
                if(cot[2] == 1):
                    sum_x_thrust += thrust
                if(cot[2] == 2):
                    sum_y_thrust += thrust
                if(cot[2] == 3):
                    sum_x_thrust -= thrust

    if(total_thrust_direction==0):
        return 0

    startx = sum_x_cot / total_thrust_direction
    starty = sum_y_cot / total_thrust_direction
    endx = startx+sum_x_thrust / total_thrust *15
    endy = starty+sum_y_thrust / total_thrust *15
    
    return startx, starty, endx, endy, total_thrust_direction/total_thrust
    

"""
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
"""

# Define a function to rotate an image by the specified angle
def rotate_image(image, angle, flipx):
    if(flipx):
        image = np.fliplr(image)
    if angle == 0:
        return image
    elif angle == 1:
        return np.rot90(image, 3)
    elif angle == 2:
        return np.rot90(image, 2)
    elif angle == 3:
        return np.rot90(image, 1)
    else:
        return image

# Define a function to insert a sprite onto the background image with a specified size and handle transparency
# Define a function to insert a sprite onto the background image with a specified size and handle transparency
def insert_sprite(background, sprite, x, y, rotation, flipx, size):
    sprite = cv2.resize(sprite, size)

    sprite = rotate_image(sprite, rotation, flipx)

    y_end, x_end, _ = sprite.shape

    # Ensure that the sprite fits within the specified region
    if y + y_end <= background.shape[0] and x + x_end <= background.shape[1]:
        # Extract the RGB channels from the sprite
        sprite_rgb = sprite[:, :, :3]

        # Extract the alpha channel from the sprite (opacity)
        alpha_channel = sprite[:, :, 3] / 255.0  # Normalize to range [0, 1]

        # Extract the corresponding region from the background
        background_region = background[y:y+y_end, x:x+x_end]

        # Blend the sprite with the background using alpha compositing
        for c in range(3):  # Iterate over RGB channels
            background_region[:, :, c] = (
                (1.0 - alpha_channel) * background_region[:, :, c]
                + alpha_channel * sprite_rgb[:, :, c]
            )

    else:
        # Handle cases where the sprite doesn't fit within the region
        print(f"Warning: Sprite at ({x}, {y}) exceeds the background dimensions.")

def sprite_position(part, position):
    #calculates the offset needed to draw a sprite at a given position
    sprite_size = part_data.parts[part["ID"]].get("sprite_size")
    if(sprite_size==None):
        return position
    #get part size
    part_size = part_data.parts[part["ID"]]["size"]
    part_rotation = part["Rotation"]
    #problematic parts on rotation 0 and 3:
    up_turret_parts=["cosmoteer.laser_blaster_small","cosmoteer.laser_blaster_large","cosmoteer.disruptor","cosmoteer.ion_beam_emitter","cosmoteer.ion_beam_prism","cosmoteer.point_defense","cosmoteer.cannon_med","cosmoteer.cannon_large","cosmoteer.cannon_deck","cosmoteer.missile_launcher","cosmoteer.railgun_launcher","cosmoteer.flak_cannon_large","cosmoteer.shield_gen_small"]
    #problematic parts on rotation 1 and 2:
    down_turret_parts=["cosmoteer.thruster_small","cosmoteer.thruster_med","cosmoteer.thruster_large","cosmoteer.thruster_huge","cosmoteer.thruster_boost"]
    #special parts:
    multiple_turrets=["cosmoteer.thruster_small_2way","cosmoteer.thruster_small_3way"]

    if(part_rotation==0 and part["ID"] in up_turret_parts):
        position[1]=position[1]-(sprite_size[1]-part_size[1])
    elif(part_rotation==3 and part["ID"] in up_turret_parts):
        position[0]=position[0]-(sprite_size[1]-part_size[1])
    elif(part_rotation==1 and part["ID"] in down_turret_parts):
        position[0]=position[0]-(sprite_size[1]-part_size[1])
    elif(part_rotation==2 and part["ID"] in down_turret_parts):
        position[1]=position[1]-(sprite_size[1]-part_size[1])
    elif(part["ID"] in multiple_turrets):
        if(part["ID"]=="cosmoteer.thruster_small_2way"):
            if(part_rotation==1):
                position[0]=position[0]-1
            if(part_rotation==2):
                position[0]=position[0]-1
                position[1]=position[1]-1
            if(part_rotation==3):
                position[1]=position[1]-1
        if(part["ID"]=="cosmoteer.thruster_small_3way"):
            if(part_rotation==0):
                position[0]=position[0]-1
            if(part_rotation==1):
                position[0]=position[0]-1
                position[1]=position[1]-1
            if(part_rotation==2):
                position[0]=position[0]-1
                position[1]=position[1]-1
            if(part_rotation==3):
                position[1]=position[1]-1
    return position

def crop(image,margin=10):
    y_nonzero, x_nonzero, _ = np.nonzero(image)
    xmin=np.min(x_nonzero)-margin
    xmax=np.max(x_nonzero)+margin
    ymin=np.min(y_nonzero)-margin
    ymax=np.max(y_nonzero)+margin
    if(xmin<0):
        xmin=0
    if(xmax>image.shape[1]):
        xmax=image.shape[1]
    if(ymin<0):
        ymin=0
    if(ymax>image.shape[0]):
        ymax=image.shape[0]
    return image[ymin:ymax,xmin:xmax]

def draw_legend(output_filename):
    """
    #create an image
    img = np.zeros((1024,1024,3), np.uint8)
    #draw a green arrow, a yellow arrow, a red arrow, a green circle
    cv2.arrowedLine(img, (300, 40), (400, 40), [0,255,0], 3, tipLength=0.3)
    cv2.arrowedLine(img, (300, 100), (400, 100), [0,255,255], 3, tipLength=0.3)
    cv2.arrowedLine(img, (300, 160), (400, 160), [0,0,255], 3, tipLength=0.3)
    cv2.circle(img, (300, 220), 10, [0,255,0], -1)
    #draw a dots size 6 at the start of the arrows
    cv2.circle(img, (300, 40), 6, [0,255,0], -1)
    cv2.circle(img, (300, 100), 6, [0,255,255], -1)
    cv2.circle(img, (300, 160), 6, [0,0,255], -1)
    #add text
    font = cv2.FONT_HERSHEY_SIMPLEX
    #center of mass next to green circle
    cv2.putText(img,'Center of Mass',(320,420), font, 0.5,(255,255,255),1,cv2.LINE_AA)
    #add white thin arrow from text to circle
    cv2.arrowedLine(img, (320, 410), (300, 400), [255,255,255], 2, tipLength=0.3)
    #save the image
    cv2.imwrite(output_filename, img)
    #show the image

    cv2.imshow('image',img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    """
    line_sep=40
    left_margin=300
    img = np.zeros((line_sep*5,600,3), np.uint8)
    #draw a green arrow, a yellow arrow, a red arrow, a green circle
    cv2.arrowedLine(img, (left_margin, line_sep*1), (left_margin+100, line_sep*1), [0,255,0], 3, tipLength=0.3)
    cv2.arrowedLine(img, (left_margin, line_sep*2), (left_margin+100, line_sep*2), [0,255,255], 3, tipLength=0.3)
    cv2.arrowedLine(img, (left_margin, line_sep*3), (left_margin+100, line_sep*3), [0,0,255], 3, tipLength=0.3)
    cv2.circle(img, (left_margin, line_sep*4), 10, [0,255,0], -1)
    #draw a dots size 6 at the start of the arrows
    cv2.circle(img, (left_margin, line_sep*1), 6, [0,255,0], -1)
    cv2.circle(img, (left_margin, line_sep*2), 6, [0,255,255], -1)
    cv2.circle(img, (left_margin, line_sep*3), 6, [0,0,255], -1)
    #add text
    font = cv2.FONT_HERSHEY_SIMPLEX
    #center of mass next to green circle
    cv2.putText(img,'Center of Mass',(left_margin+20,line_sep*4+5), font, 0.5,(255,255,255),1,cv2.LINE_AA)
    #add white thin arrow from text to circle
    cv2.arrowedLine(img, (left_margin+20, line_sep*4), (left_margin, line_sep*4), [255,255,255], 2, tipLength=0.2)
    #center of thrust to the left of green arrow
    cv2.putText(img,'Center of Thrust',(left_margin-200,line_sep*1+5), font, 0.5,(255,255,255),1,cv2.LINE_AA)
    #add white thin arrow from text to start of green arrow
    cv2.arrowedLine(img, (left_margin-50, line_sep*1), (left_margin, line_sep*1), [255,255,255], 2, tipLength=0.2)
    #strafe center of thrust to the left of yellow arrow
    cv2.putText(img,'Strafe Center of Thrust',(left_margin-250,line_sep*2+5), font, 0.5,(255,255,255),1,cv2.LINE_AA)
    #add white thin arrow from text to start of yellow arrow
    cv2.arrowedLine(img, (left_margin-50, line_sep*2), (left_margin, line_sep*2), [255,255,255], 2, tipLength=0.2)
    #engine center of thrust to the left of red arrow
    cv2.putText(img,'Engine Center of Thrust',(left_margin-250,line_sep*3+5), font, 0.5,(255,255,255),1,cv2.LINE_AA)
    #add white thin arrow from text to start of red arrow
    cv2.arrowedLine(img, (left_margin-50, line_sep*3), (left_margin, line_sep*3), [255,255,255], 2, tipLength=0.2)
    #to the right of the arrows, add "length of arrow depends on thrust" on 3 lines
    cv2.putText(img,'length of vector',(left_margin+120,line_sep*1+5), font, 0.5,(255,255,255),1,cv2.LINE_AA)
    cv2.putText(img,'depends on thrust',(left_margin+120,line_sep*2+5), font, 0.5,(255,255,255),1,cv2.LINE_AA)
    cv2.putText(img,'on that direction',(left_margin+120,line_sep*3+5), font, 0.5,(255,255,255),1,cv2.LINE_AA)
    #save the image
    cv2.imwrite(output_filename, img)
    #show the image
    #cv2.imshow('image',img)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

def draw_ship(parts, data_com, data_cot, ship_orientation, output_filename):
    #use opencv to draw ship
    #create blank image factor times of the ship
    sprite_square_size = 64
    size_factor = round(sprite_square_size/4)
    square_size = round(size_factor)
    img = np.zeros((120*size_factor,120*size_factor,3), np.uint8)

    """
    BLUE_PARTS= ["cosmoteer.shield_gen_small","cosmoteer.shield_gen_large","cosmoteer.control_room_small","cosmoteer.control_room_med","cosmoteer.control_room_large", "cosmoteer.armor", "cosmoteer.armor_2x1","cosmoteer.armor_wedge","cosmoteer.armor_1x2_wedge","cosmoteer.armor_1x3_wedge","cosmoteer.armor_tri","cosmoteer.armor_structure_hybrid_1x1","cosmoteer.armor_structure_hybrid_1x2","cosmoteer.armor_structure_hybrid_1x3","cosmoteer.armor_structure_hybrid_tri"]
    GREY_PARTS= ["cosmoteer.structure","cosmoteer.structure_wedge","cosmoteer.structure_1x2_wedge","cosmoteer.structure_1x3_wedge","cosmoteer.structure_tri","cosmoteer.corridor","cosmoteer.fire_extinguisher","cosmoteer.airlock","cosmoteer.crew_quarters_small","cosmoteer.crew_quarters_med","cosmoteer.conveyor","cosmoteer.storage_2x2","cosmoteer.storage_3x2","cosmoteer.storage_3x3","cosmoteer.storage_4x3","cosmoteer.storage_4x4"]
    THRUSTERS= ["cosmoteer.thruster_small","cosmoteer.thruster_med","cosmoteer.thruster_large","cosmoteer.thruster_small_2way","cosmoteer.thruster_small_3way","cosmoteer.thruster_huge","cosmoteer.thruster_boost"]
    YELLOW_PARTS= THRUSTERS+["cosmoteer.power_storage","cosmoteer.engine_room","cosmoteer.reactor_small","cosmoteer.reactor_med","cosmoteer.reactor_large"]
    RED_PARTS= ["cosmoteer.laser_blaster_small","cosmoteer.laser_blaster_large","cosmoteer.disruptor","cosmoteer.ion_beam_emitter","cosmoteer.ion_beam_prism","cosmoteer.tractor_beam_emitter","cosmoteer.point_defense","cosmoteer.mining_laser_small","cosmoteer.cannon_med","cosmoteer.cannon_large","cosmoteer.cannon_deck","cosmoteer.explosive_charge","cosmoteer.missile_launcher","cosmoteer.railgun_loader","cosmoteer.railgun_accelerator","cosmoteer.railgun_launcher","cosmoteer.flak_cannon_large"]
    #add parts to image
    for part in parts:
        x_coord = part["Location"][0] +60
        y_coord = part["Location"][1] +60
        if(part["ID"] in THRUSTERS and thruster_touching_engine_room(parts,part)):
            color = [0,200,200] #thrusters touching engine room are light yellow
        elif(part["ID"] in BLUE_PARTS):
            color = [125,0,0]#armor shields and control rooms are blue
        elif(part["ID"] in GREY_PARTS):
            color = [125,125,125]#structure and hull is grey
        elif(part["ID"] in YELLOW_PARTS):
            color = [0, 125, 125]#thrusters and reactors are yellow
        elif(part["ID"] in RED_PARTS):
            color=[0,0,125]#weapons are red
        else:
            color = [125,0,125]#everything else is purple
        size=part_data.parts[part["ID"]]["size"]
        rotation=part["Rotation"]
        if(rotation==1 or rotation==3):
            size=(size[1],size[0])
        #size=(1,1)
        
        
        for i in range(size[0]):
            for j in range(size[1]):
                cv2.rectangle(img, (round((x_coord+i)*size_factor+1), round((y_coord+j)*size_factor+1)),
                                (round((x_coord+i+1)*size_factor-1), round((y_coord+j+1)*size_factor-1)),
                                color, -1)
    """

    #using sprites instead of rectangles
    for i in range(len(parts)):
        if(parts[i]["ID"] in ["cosmoteer.cannon_deck","cosmoteer.ion_beam_prism"]):
            parts.append(parts.pop(i))#move top turrets to the end of the list so they are drawn last
    for part in parts:
        x_coord = part["Location"][0] +60
        y_coord = part["Location"][1] +60
        size=part_data.parts[part["ID"]]["size"]
        rotation=part["Rotation"]
        flipx=part["FlipX"]

        x_coord,y_coord=sprite_position(part, [x_coord, y_coord])

        sprite_path="sprites/"+part["ID"].replace("cosmoteer.","")+".png"
        img_part = cv2.imread(sprite_path, cv2.IMREAD_UNCHANGED)
        #print(img_part.shape)
        insert_sprite(img, img_part, round(x_coord*size_factor),round(y_coord*size_factor) , rotation,flipx, (round(img_part.shape[1]/4), round(img_part.shape[0]/4)))
    #the image should be a bit darker
    img=img*0.8

    if(DRAW_COM):
        #add center of mass (as a green circle)
        cv2.circle(img, (round((data_com[0]+60)*size_factor), round((data_com[1]+60)*size_factor)), square_size, [0,255,0], -1)
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
                part_rotation = cot[1]
                vector=cot[0]
                end_point = (0,0)
                if(part_rotation==0):
                    end_point = (vector.x, vector.y-2)
                elif(part_rotation==1):
                    end_point = (vector.x+2, vector.y)
                elif(part_rotation==2):
                    end_point = (vector.x, vector.y+2)
                elif(part_rotation==3):
                    end_point = (vector.x-2, vector.y)
                
                
                cv2.arrowedLine(img, (round((vector.x+60)*size_factor), round((vector.y+60)*size_factor)), (round((end_point[0]+60)*size_factor), round((end_point[1]+60)*size_factor)), [0,0,255], 2, tipLength=0.3)
                #also draw a dot at the start of the arrow
                cv2.circle(img, (round((vector.x+60)*size_factor), round((vector.y+60)*size_factor)), 3, [0,0,255], -1)
    
    #draw center of thrust of the ship
    if(DRAW_COTS):
        origin_thrust,thrust_vector,thrust_direction=data_cot
        total_thrust=sum(thrust_direction)

        #print("ship_orientation", ship_orientation)
        origin_thrust.append(origin_thrust.pop(ship_orientation))
        thrust_vector.append(thrust_vector.pop(ship_orientation))
        thrust_direction.append(thrust_direction.pop(ship_orientation))
        size_of_arrow=20
        #print the vectors

        for i in range(8):
            start=(origin_thrust[i]+60)*size_factor
            #print("start", start)
            start=(round(start.x),round(start.y))
            #reduce size of vector
            if(thrust_vector[i].length==0):
                continue
            thrust=(thrust_vector[i]-origin_thrust[i])/total_thrust
            end=thrust*size_of_arrow+origin_thrust[i]
            end=(end+60)*size_factor
            #print("end", end)
            end=(round(end.x),round(end.y))
            #print(i)
            if(i==7):
                arrow_color=[0,200,0]
            else:
                arrow_color=[0,255,255]
            cv2.arrowedLine(img, start,end, arrow_color,2, tipLength=0.2)
            cv2.circle(img, start, 3, arrow_color, -1)
        
        #restore the order of the lists
        origin_thrust.insert(ship_orientation,origin_thrust.pop())
        thrust_vector.insert(ship_orientation,thrust_vector.pop())
        thrust_direction.insert(ship_orientation,thrust_direction.pop())
                
    #crop image (remove the black border around the ship)
    img=crop(img)

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
    comx,comy,mass = list(center_of_mass(parts))
    data_com = [comx,comy,mass]
    #calculate center of thrust
    ship_orientation = cosmoteer_save_tools.Ship(SHIP).data["FlightDirection"]
    origin_thrust,thrust_vector,thrust_direction=center_of_thrust(parts)
    origin_thrust,thrust_vector,thrust_direction=diagonal_center_of_thrust(origin_thrust,thrust_vector,thrust_direction)
    data_cot=[origin_thrust,thrust_vector,thrust_direction]
    #calculate speed
    
    #print("center of thrust: ", data_cot)
    speed=top_speed(mass,thrust_direction[ship_orientation])

    draw_ship(parts, data_com, data_cot, ship_orientation, output_filename)#writes to out.png

    print("center of mass: ", data_com)

    for i in range(8):
        print("center of thrust in direction", i, ": ", data_cot[0][i])
        print("thrust vector in direction", i, ": ", data_cot[1][i])
        print("thrust in direction", i, ": ", data_cot[2][i])
        print()

    print("speed: ", speed)

    print("ship_orientation", thrust_direction)

    return data_com, data_cot, speed

if(__name__ == "__main__"):
    com(SHIP, "out.png")


