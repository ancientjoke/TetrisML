import marshal
import dis
import os
pyc_dir = 'pyc_temp'
header_size = 16
for filename in os.listdir(pyc_dir):
    if filename.endswith('.pyc'):
        path = os.path.join(pyc_dir, filename)
        print(f'\nDisassembly for {filename}:')
        with open(path, 'rb') as f:
            f.read(header_size)
            code = marshal.load(f)
            dis.dis(code)
