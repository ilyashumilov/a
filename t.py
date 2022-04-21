with open('france_top.txt', 'r', encoding='utf-8') as f:
    france = f.read().strip().split('\n')

d = []
for i in france:
    d.append(i.split(':')[0])


with open('france_top_ids.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(d))
