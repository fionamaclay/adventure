"""Pick back up with 10.4 A #2, string formatting for next time"""

from console import fg
from console import bg
from console import fx

import re
import textwrap

WIDTH = 60
MARGIN = "  "

"""
  =========
  World Map
  =========

            market
              |
  home -- town square -- woods -- hill
              |                    |
            bakery                cave

"""
DEBUG = False

PLAYER = {
    "place": "home" ,
    "inventory": {
        "gems": 50 ,
    } ,
}

PLACES = {
    "home": {
        "key": "home" , 
        "name": "Your cottage" ,
        "east": "town-square" ,
        "description": "Your humble bode and an ideal place to rest after tiresome adventures." ,
        "items": ["book" , "desk"] ,
    },
    "town-square": {
        "key": "town-square" ,
        "name": "The Town Square" ,
        "west": "home" ,
        "east": "woods" ,
        "north": "market" ,
        "south": "bakery" ,
        "description": "The hustlin' and bustlin' meeting place for the town." ,
    },
    "market": {
        "key": "market" ,
        "name": "The Market" ,
        "south": "town-square" ,
        "description": "The market is where you can go to shop for items relevant to your quest." ,
        "items": ["potion" , "sword" , "pillow"] ,
        "can": ["shop" , "buy"]
    },
    "bakery": {
        "key": "bakery" ,
        "name": "The Bakery" ,
        "north": "town-square" ,
        "description": "The Bakery is the place to visit when in need of a sweet treat to fuel you for your journey." ,
    },
    "woods": {
        "key": "woods" ,
        "name": "The Woods" ,
        "west": "town-square" ,
        "east": "hill" ,
        "description": "The woods are shady, mysterious, and full of clues for your journey." ,
    },
    "hill": {
        "key": "hill" ,
        "name": "The Hill" ,
        "west": "woods" ,
        "south": "cave" ,
        "description": "A large hill on the outskirts of town; the perfect place to overlook the town." ,
    },
    "cave": {
        "key": "cave" ,
        "name": "The Cave" ,
        "north": "hill" ,
        "description": "A large, dark cave a ways away from town. What lies inside is a mystery..." ,
    },
}

ITEMS = {
    "potion": {
        "key": "potion",
        "name": 'Battle Potion',
        "description": "A potion that damages the health of one's enemies",
        "price": -10,
    },
    "sword": {
        "key": "sword",
        "name": "Battle Sword",
         "description": "A large, pure silver sword to slay one's enemies",
         "price": -11,
    },
    "pillow": {
         "key": "pillow",
         "name": "Plush Pillow",
         "description": "A soft pillow used to rest after tiresome quests",
         "price": -5,
    },
    "desk" : {
        "key": "desk" ,
        "name": "Desk" ,
        "description": "A wooden desk with a large leather-bound book open on its surface" ,
    },
    "book": {
        "key": "book" ,
        "name": "Book" ,
        "description": "A leather-bound book open to an interesting passage..." ,
        "can_take": True ,
        "can_read": True ,
        "passage": "The rainbow is fading, with dissipating hues. \nYour journey will be arduous, like the fierce ocean blue. \nYou may be triumphant, and rest again in your bed, \nhowever first you must bargain with the dog with three heads." ,
    },
    "gems": {
        "key": "gems" ,
        "name": "Gems" ,
        "description": "The currency used to buy things" ,
    }
}

def do_shop():
    """ To list items for sale """
    if not place_can("shop"):
        error("Sorry, you can't shop here.")
        return
    
    place = get_place()
   
    header(f'{fg.blue("Items for Sale!")}')

    for key in place.get("items", []):
        item = get_item(key)
        if not is_for_sale(item):
            continue
        write(f"{item['name']}: {item['description']} {abs(item['price'])}")
    
def do_quit():
    """ To exit the game """
    write("Goodbye.")
    quit()

def do_go(args):
    """ To move somewhere else """
    debug(f"Trying to go: {args}")
    if not args:
        error("Which way do you want to go?")
        return
    
    direction = args[0].lower()

    if direction not in ("north", "south", "east", "west"):
        error(f"Sorry, I don't know how to go: {direction}")
        return

    old_place = get_place()
    new_name = old_place.get(direction)
    
    if not new_name:
        error(f"Sorry, you can't go {direction} from here.")
        return

    new_place = get_place(new_name)

    PLAYER['place'] = new_name

    header(new_place['name'])
    wrap(new_place['description'])


def do_examine(args):
    """ To examine an object """
    debug(f"Trying to examine: {args}")
    if not args:
        error("What do you want to examine?")
        return
    
    place = get_place()

    name = args[0].lower()

    if not place_has(name) and not player_has(name):
        error(f"Sorry, I don't know what {name} is.")
        return

    item = get_item(name)

    header(item["name"])
    wrap(item["description"])


def do_look():
    """ To look around your current location"""
    debug("Trying to look around.")

    place = get_place()

    header(place["name"])
    wrap(place["description"])

    items = place.get("items", [])

    if items:
        names = []
        for key in items:
            item = get_item(key)
            names.append(item["name"])
        last = names.pop()
        text = ", ".join(names)
        if text:
            text = text + " and " + last
        
        print()
        write(f"You see {text}.")
    
    print()
    
    for direction in ("north" , "south" , "east" , "west"):
        name = place.get(direction)
        if not name:
            continue
        destination = get_place(name)
        write(f"To the {direction} is {destination['name']}.")

def do_take(args):
    """To take an item from your current location"""
    debug(f"Trying to take {args}.")
    
    if not args:
        error("What would you like to take?")
        return

    place = get_place()

    name = args[0].lower()

    if not place_has(name):
        error(f"Sorry, I don't see a {name} here.")
        return

    item = get_item(name)

    if not item.get('can_take'):
        wrap(f"You try to pick up {item['name']}, but you find your muscles to be too feeble to lift it!")
        return
    
    inventory_change(name)
    place_remove(name)

    wrap(f"You pick up {item['name']} and put it in your pack.")

def do_inventory():
    """To look inside your inventory"""
    debug("Trying to show inventory...")
    header("INVENTORY")

    if not PLAYER["inventory"]:
        write("Empty.")
        return

    for name , qty in PLAYER["inventory"].items():
        item = get_item(name)
        write(f"{item['name']}: {qty}")
        
    print()

def do_drop(args):
    """To drop an item from your inventory"""
    debug(f"Trying to drop {args}.")

    if not args:
        error("What would you like to drop?")
        return

    name = args[0].lower()

    if not player_has(name):
        error(f"You do not have any {name}.")
        return
    
    qty = PLAYER["inventory"][name]
    inventory_change(name, -qty)

    place_add(name)
    
    wrap(f"You set down {name}.")

def do_read(args):
    """To read something"""
    if not args:
        error("What would you like to read?")
        return

    place = get_place()

    name = args[0].lower()

    if name not in place.get("items" , []):
        error(f"Sorry, I don't see a {name} to read here.")
        return

    item = get_item(name)

    if not item:
        abort(f"Whoops! The information about {name} seems to be missing.")

    if not item.get('can_read'):
        error(f"It seems you cannot read {item['name']}.")
        return

    if item.get('can_read'):
        text = item.get('passage')
        lines = text.splitlines()

        header("It reads: ")

        for line in lines:
            wrap(line)

def do_buy(args):
    debug(f"Trying to buy {args}.")

    if not place_can("buy"):
        error("Sorry, you can't buy things here.")
        return

    if not args:
        error("What would you like to buy?")
        return

    name = args[0].lower()

    if not place_has(name):
        error(f"Sorry, I don't see a {name} here.")
        return

    item = get_item(name)
    if not is_for_sale(item):
        error(f"Sorry, {name} is not for sale.")
        return

    price = abs(item["price"])
    if not player_has("gems", price):
        gems = PLAYER["inventory"].get("gems", 0)
        error(f"Sorry, you can't afford {name} because you only have {gems}.")
        return

    inventory_change("gems", -price)
    inventory_change(name)

    place_remove(name)

    write(f"You bought {name}.")

def get_place(key=None):
    if not key:
        key = PLAYER["place"]
        
    place = PLACES.get(key)

    if not place:
        abort(f"Woops! The information about {key} seems to be missing.")
    
    return place

def get_item(key):
    item = ITEMS.get(key)
    
    if not item:
        abort(f"Whoops! The information about {key} seems to be missing.")
        return
    
    return item

def is_for_sale(item):
    if "price" in item:
        return True
    else:
        return False

def inventory_change(key, quantity=1):
    PLAYER["inventory"].setdefault(key, 0)

    PLAYER["inventory"][key] = PLAYER["inventory"][key] + quantity

    if not PLAYER["inventory"][key] or PLAYER["inventory"][key] <= 0:
        PLAYER["inventory"].pop(key)

def player_has(key, qty=1):
    if key in PLAYER["inventory"] and PLAYER["inventory"][key] >= qty:
        return True
    else:
        return False

def place_has(item):
    place = get_place()
    if item in place.get("items", []):
        return True
    else:
        return False

def place_add(key):
    place = get_place()
    place.setdefault("items", [])

    if key not in place["items"]:
        place["items"].append(key)

def place_remove(key):
    place = get_place()

    if key in place.get("items", []):
        place["items"].remove(key)

def place_can(action):
    place = get_place()

    if action in place.get("can", []):
        return True
    else:
        return False

def abort(message):
    """To send an error message and exit the program when there is an issue in the code"""
    error(message)
    exit(1)

def main():
    print("Welcome!")
    while True:
        debug(f"You are at: {PLAYER['place']}")
        
        reply = input("> ").strip()
        args = reply.split()

        if not args:
            continue

        command = args.pop(0)

        debug(f"Command: {command}, Args: {args}")

        if command == "q" or command == "quit":
            do_quit()
        elif command == "shop":
            do_shop()
        elif command == "g" or command == "go":
            do_go(args)
        elif command == "x" or command == "exam" or command == "examine":
            do_examine(args)
        elif command == "l" or command == "look":
            do_look()
        elif command == "t" or command == "take" or command == "grab":
            do_take(args)
        elif command == "i" or command == "inventory":
            do_inventory()
        elif command == "drop":
            do_drop(args)
        elif command == "read" or command == "r":
            do_read(args)
        elif command == "buy":
            do_buy(args)
        else:
            error("No such command.")
            continue
        
def debug(message):
    if DEBUG:
        print("DEBUG: ", message)

def error(message):
    print(f"{fg.red('Error: ')} {message}")

def wrap(text):
    paragraph = textwrap.fill(
        text,
        WIDTH,
        initial_indent = MARGIN,
        subsequent_indent = MARGIN,
    )
    print(paragraph)

def write(text):
    print(MARGIN, text)

def header(title):
    print()
    write(f"{fx.bold(title)}")
    print()

if __name__ == "__main__":
    main()
    

