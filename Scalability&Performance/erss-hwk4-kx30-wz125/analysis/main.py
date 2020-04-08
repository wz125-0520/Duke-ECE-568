import matplotlib.pyplot as plt
import sys


# Read a file line by line and return list of lines.
def read_file(filename):
    f = open(filename, "r")
    lines = f.readlines()
    f.close()
    return lines


# Parse the log file line by line.(strictly follow our print format)
def parse_log(filename):
    lines = read_file(filename)
    data = []
    for l in lines:
        data.append(int(l.split(":")[1]))
    return data


# Use data as y value to draw the image.
def draw(data):
    plt.ylim(min(data) - 5, max(data) + 5)
    plt.plot(data, marker="o")
    plt.show()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        for index in range(1, len(sys.argv)):
            draw(parse_log(sys.argv[index]))
    draw(parse_log("./data.log"))
