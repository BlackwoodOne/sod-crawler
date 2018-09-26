import json
import os

##Util function to load the filelist
def load_list(filename):
    lines = []
    if(os.path.isfile(filename)):
        with open(filename, encoding='utf-8') as f:

            for line in f:
                line = line.rstrip()
                if not line.startswith('#') and not len(line) == 0:
                    lines.append(line)
    else:
        print("File does not exist! "+ filename)
    return lines

##Util function to load the filelist
def load_line(filename):
    text = ""
    if (os.path.isfile(filename)):
        with open(filename, encoding='utf-8') as f:
            text = ""
            for line in f:
                line = line.rstrip()
                if not line.startswith('#') and not len(line) == 0:
                    text= text + line
    else:
        print("File does not exist! "+ filename)
    return text

##Util function to write one line
def write_line(filename,data):
    with open(filename, 'w') as f:
            f.write(data)
    print(("Data written to " + filename))


##Util function to write the filelist
def write_list(filename, lines):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    print("List written " + filename)

def write_json(filename,data):
    with open(filename, "w") as write_file:
        json.dump(data, write_file, indent=4)

##Util function clear file
def clearFile(filename):
    with open(filename, 'w') as f:
            f.write("")
    print(("File cleared: " + filename))