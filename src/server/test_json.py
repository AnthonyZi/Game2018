import json

a = dict()
a["playername"] = "Assax"

a["ready"] = True

a["game"] = dict()
a["game"]["player_dx"] = -1
a["game"]["player_dy"] = +1
a["game"]["action"]    = "search"
a["game"]["pi"]        = 3.14

print(a)
b = json.dumps(a)

print("")

print(b)

print("")

c = json.loads(b)
for ckey in c.keys():
    print(c[ckey])
    if isinstance(c[ckey], dict):
        d = c[ckey]
        for dkey in d.keys():
            print(d[dkey])
            if isinstance(d[dkey], int):
                print("integer")
            if isinstance(d[dkey], float):
                print("float")
            if isinstance(d[dkey], str):
                print("string")
print(c)
