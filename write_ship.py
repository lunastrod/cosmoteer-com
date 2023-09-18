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
import gzip

def read_lsb(image_path):
    try:
        # Open the image
        img = Image.open(image_path)

        # Initialize a list to store the LSBs of each channel
        lsb_bytes = bytearray()

        # Iterate over each pixel
        for y in range(img.height):
            for x in range(img.width):
                pixel_values = img.getpixel((x, y))
                for i in range(3):  # Iterate over Red, Green, Blue channels
                    pixel_value = pixel_values[i]
                    # Extract the LSB of the pixel value and append it to the bytearray
                    lsb_bytes.append(pixel_value & 1)

        # Convert the bytearray to bytes
        lsb_bytes = bytes(lsb_bytes)

        return lsb_bytes

    except Exception as e:
        print("An error occurred:", str(e))
        return None

if __name__ == "__main__":
    image_path = "ships/Sion.ship.png"  # Replace with the path to your image
    lsb_bytes = read_lsb(image_path)

    if lsb_bytes is None:
        print("LSB extraction failed.")
        exit()
    print("decompressing...")
    print(lsb_bytes)
    lsb_bytes=gzip.decompress(lsb_bytes)
    print("LSBs of the image as a bytearray:")
    print(lsb_bytes)
