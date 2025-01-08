

with open("Damcon_Names.txt", "r") as f:
    output = ""
    for line in f:
        newentry = line.replace(",", "")
        completeentry = newentry.replace(".", "")
        output += f"{completeentry}"


with open("Damcon_Names.txt", "w") as f:
    for name in output:
        f.write(name)

