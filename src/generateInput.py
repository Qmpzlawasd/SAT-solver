import random

for _ in range(3):
    for i in range(0x20, 0x7F):
        print(random.choice([f'-{chr(i)}', f'{chr(i)}']),
              random.choice(['\n']+[' ']*2), sep='', end='')
