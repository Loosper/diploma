import sys

def format(data):
    print('(')
    for line in data:
        if line == '':
            continue
        print(f'    \'{line}\\n\'')
    print(')')


data = ''
sep = sys.argv[2]
with open(sys.argv[1], 'r') as file:
    data = file.read()

data = data.split('\n')
mid = data.index(sep)


print('here\'s something to get you started')
format(data[:mid])
format(data[mid:])
