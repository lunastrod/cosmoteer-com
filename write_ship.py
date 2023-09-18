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