import re

def matchingField(field):
    if "bañ" in field:
        return "bathromms", re.findall(r'[0-9]+', field)
    elif "garaje" in field:
        return "parking", True
    elif "ascensor" in field:
        return "elevator", True
    elif "Piscina" in field:
        return "pool", True
    elif "Trastero" in field:
        return "storage_room", True
    elif "Terraza" in field:
        return "terraze", True
    else:
        return None

def machingPpalFieldFotoCasa(field, value):
    print("Field %s, Value %s" % (field, value))
    if "inmueble" in field:
        return "type", value
    elif "Parking " in field:
        return "parking", True
    elif "Ascensor" in field:
        return "elevator", True
    else:
        return None

def machingAuxFieldFotoCasa(field):
    if "Piscina" in field:
        return "pool", True
    elif "Trastero" in field:
        return "storage_room", True
    elif "Terraza" in field:
        return "terraze", True
    else:
        None

def checkFotoCasaFieldFound(data_home):
    if not data_home.get("type"):
        data_home["type"] = "N/A"
    if not data_home.get("parking"):
        data_home["parking"] = False
    if not data_home.get("elevator"):
        data_home["elevator"] = False
    if not data_home.get("pool"):
        data_home["pool"] = False
    if not data_home.get("storage_room"):
        data_home["storage_room"] = False
    if not data_home.get("terraze"):
        data_home["terraze"] = False

    return data_home