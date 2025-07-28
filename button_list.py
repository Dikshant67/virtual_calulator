button_list = []
labels = [
    ['7', '8', '9', '/'],
    ['4', '5', '6', '*'],
    ['1', '2', '3', '-'],
    ['C', '0', '=', '+']

for i in range(len(labels)):
    for j in range(len(labels[i])):
        x = 100 * j + 50  # Move left side
        y = 100 * i + 200  # Push it down a bit
        button_list.append(Button((x, y), 100, 100, labels[i][j]))

