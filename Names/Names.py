import os


def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

shuttleDatabase = set()
teamleaderDatabase = set()

with open(find("Shuttle_Names_List.txt", os.getcwd()), "r") as f:
    for line in f:
        #print(line.strip())
        shuttleDatabase.add(line.strip())

with open(find("Damcon_Names.txt", os.getcwd()), "r") as f:
    for line in f:
        #print(line.strip())
        teamleaderDatabase.add(line.strip())
