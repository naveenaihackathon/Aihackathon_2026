import json

with open('soln.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

print(f'Notebook has {len(nb["cells"])} cells')
print('\nCell types and approximate content:')
for i, cell in enumerate(nb['cells']):
    cell_type = cell['cell_type']
    if cell_type == 'code':
        source = ''.join(cell['source'])[:70]
        print(f'\nCell {i}: [CODE]')
        print(f"  {source}")
    else:
        source = ''.join(cell['source'])[:70]
        print(f'\nCell {i}: [MARKDOWN]')
        print(f"  {source}")
