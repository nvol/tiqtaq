import json
import main as tt

with open('tiqtaq.json') as f:
    j = json.load(f)
gs = [[int(i) for i in g] for g in j]

# # look for symmetrical combinations
# for g in gs:
#     symm = tt.transform(g, 'd')
#     if symm in gs:
#         print('ALARM!', g, symm)

print('dict len:', len(j))
print('   X won:', tt.filter(j, 1))
print('   O won:', tt.filter(j, -1))
print('    draw:', tt.filter(j, 0))

