"""
stat_analysis.py

A simple script for viewing income data from raw log data provided by the bot.
"""

import re

import matplotlib.pyplot as plt

i = 0
with open('raw_ash.txt', 'r', encoding='utf-8') as file:
    working = {'work': 0, 'slut': 0, 'crime': 0, 'total': 0}
    changes = {'work': [0], 'slut': [0], 'crime': [0], 'total': [0]}
    matches = re.finditer(
        r'\[[0-9-:, ]+\] \[\w+\] \[\w+\] Executing \$(work|crime|slut) task.\n\[[0-9-:, ]+\] \[\w+\] \[\w+\] (Gained|Lost) \$(\d+)',
        file.read())

    for match in matches:
        task, sign, change = match.group(1), match.group(2) == 'Lost', int(match.group(3))
        if sign:
            change *= -1
        print(task, sign, change)

        working[task] += int(change)
        working['total'] += int(change)
        for key in changes.keys():
            changes[key].append(working[key])
            # changes[key].append(max(0, working[key]))

print('Finished processing datafile.')

for k, v in working.items():
    print(f'{k} earned {v}.')
print(f'{sum(working.values())} earned total.')

fig, ax = plt.subplots()
xaxis = list(range(len(changes['work'])))
for k, v in changes.items():
    ax.plot(xaxis, v, label=k)
# ax.stackplot(, changes.values(), labels=changes.keys())
ax.legend(loc='upper left')
ax.set_title('Earnings by Task over time')
ax.set_xlabel('Tasks')
ax.set_ylabel('Earnings ($)')

plt.show()
