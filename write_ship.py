from cosmoteer_save_tools import Ship

"""

print(ship.data.keys())
print()
print(ship.data["Author"])
#print(ship.data["BuildCenterlineNESW"])
#print(ship.data["BuildCenterlineNWSE"])
#print(ship.data["BuildCenterlineX"])
#print(ship.data["BuildCenterlineY"])

#print(ship.data["CrewSourceTargets"])
#print(ship.data["Decals1"])
#print(ship.data["Decals2"])
#print(ship.data["Decals3"])
print(ship.data["DefaultAttackFollowAngle"]) #None
print(ship.data["DefaultAttackRadius"]) #None
print(ship.data["DefaultAttackRotation"]) #None
print(ship.data["Description"]) #unset
print(ship.data["Doors"]) #unset
print(ship.data["FlightDirection"]) #1
print(ship.data["FormationOrder"]) #3
print(ship.data["Name"]) #unnamed ship
print(ship.data["NewFlexResourceGridTypes"]) #unset
#print(ship.data["PaintCenterlineNESW"])
#print(ship.data["PaintCenterlineNWSE"])
#print(ship.data["PaintCenterlineX"])
#print(ship.data["PaintCenterlineY"])
print(ship.data["PartControlGroups"]) #unset
print(ship.data["Parts"])
print(ship.data["PartUIColorValues"]) #unset
print(ship.data["PartUIToggleStates"]) #unset
print(ship.data["ResourceConsumptionToggles"]) #unset
print(ship.data["ResourceSupplierTargets"]) #unset
print(ship.data["ResourceSupplyToggles"]) #unset
#print(ship.data["Roles"])
print(ship.data["RoofBaseColor"]) #('0000803F', '28CD643F', '8AF5213F', '0000803F')
print(ship.data["RoofBaseTexture"]) # camo
print(ship.data["RoofDecalColor1"]) #('0000803F', '28CD643F', '8AF5213F', '0000803F')
print(ship.data["RoofDecalColor2"]) #('0000803F', '28CD643F', '8AF5213F', '0000803F')
print(ship.data["RoofDecalColor3"]) #('0000803F', '28CD643F', '8AF5213F', '0000803F')
print(ship.data["ShipRulesID"]) #cosmoteer.terran
print(ship.data["Version"]) #3
print(ship.data["WeaponDirectControlBindings"]) #unset
print(ship.data["WeaponSelfTargets"]) #unset
print(ship.data["WeaponShipRelativeTargets"]) #unset
"""
"""
from PIL import Image

#ship=Ship("ships/engine.ship.png")
new_ship=Ship("ships/engine.ship.png")
new_ship.write()
#print(ship.data)
"""
"""
from PIL import Image
import numpy as np
import gzip

def read_bytes(image_data) -> bytes:
    data = [byte for pixel in image_data for byte in pixel[:3]]
    length = int.from_bytes(bytes([get_byte(i, data) for i in range(4)]), "big")
    return bytes([get_byte(i + 4, data) for i in range(length)])

def get_byte(offset, data) -> int:
    out_byte = 0
    for bits_right in range(8):
        out_byte |= (data[offset * 8 + bits_right] & 1) << bits_right
    return out_byte

if __name__ == "__main__":
    image_path = "ships/engine.ship.png"  # Replace with the path to your image
    try:
        # Open the image in the main function
        img_data=np.array(Image.open(image_path).getdata())
        data=read_bytes(img_data)
        if data[:9] == b'COSMOSHIP':
            data = data[9:]
            version = 2
        print(data)
        uncompressed_data = gzip.decompress(data)
        print(uncompressed_data)
    except Exception as e:
        print("An error occurred while opening the image:", str(e))

        ['Author', 'BuildCenterlineNESW', 'BuildCenterlineNWSE', 'BuildCenterlineX', 'BuildCenterlineY', 'CrewSourceRoles', 'CrewSourceTargets', 'Decals1', 'Decals2', 'Decals3', 'DefaultAttackFollowAngle', 'DefaultAttackRadius', 'DefaultAttackRotation', 'Description', 'Doors', 'FlightDirection', 'FormationOrder', 'Name', 'NewFlexResourceGridTypes', 'PaintCenterlineNESW', 'PaintCenterlineNWSE', 'PaintCenterlineX', 'PaintCenterlineY', 'PartControlGroups', 'Parts', 'PartUIColorValues', 'PartUIToggleStates', 'ResourceConsumptionToggles', 'ResourceSupplierTargets', 'ResourceSupplyToggles', 'Roles', 'RoofBaseColor', 'RoofBaseTexture', 'RoofDecalColor1', 'RoofDecalColor2', 'RoofDecalColor3', 'ShipRulesID', 'Version', 'WeaponDirectControlBindings', 'WeaponSelfTargets', 'WeaponShipRelativeTargets']

"""
from PIL import Image

image_path = "ships/targeted_prism.ship.png"  # Replace with the path to your image
my_ship1=Ship(image_path)
#print(my_ship.__str__()[:1000])
new_image=my_ship1.write(Image.open("ships/huh.ship.png"))
#save the image
new_image.save("ships/out.ship.png")

my_ship2=Ship("ships/out.ship.png")
print(my_ship1.raw_data==my_ship2.raw_data)
#print the data around the first difference in hex
for i in range(len(my_ship1.raw_data)):
    if my_ship1.raw_data[i]!=my_ship2.raw_data[i]:
        #print(my_ship1.raw_data[i-100:i+100])
        #print the bytes separated by spaces but if the byte is a character, print the character
        print(" ".join([chr(x) if x>=32 and x<=126 else hex(x) for x in my_ship1.raw_data[i-100:i+50]]))
        #print(" ".join([hex(x) for x in my_ship1.raw_data[i-100:i+50]]))
        print("===================================")
        print(" ".join([chr(x) if x>=32 and x<=126 else hex(x) for x in my_ship2.raw_data[i-100:i+50]]))
        #print(" ".join([hex(x) for x in my_ship2.raw_data[i-10:i+50]]))
        break

print(my_ship1.data==my_ship2.data)
#print all of the differences
for key in my_ship1.data.keys():
    if my_ship1.data[key]!=my_ship2.data[key]:
        print(key)
        print(my_ship1.data[key])
        print("===================================")
        print(my_ship2.data[key])
        print()
