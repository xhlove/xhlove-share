import re
import json
from pathlib import Path


def gen_func(func_name: str, import_line: str):
    signature = re.findall('\([^()]*\)', import_line)
    if len(signature) == 0:
        print(f'匹配签名失败 => {import_line}')
        return
    param = ''
    _param = ''
    result = ''
    for item in signature:
        items = item.strip('()').split(' ')
        if items[0] == 'param':
            param = ', '.join([f'Type.{_.upper()}' for _ in items[1:]])
            _param = ', ' + ', '.join([f'param_{index}' for index, _ in enumerate(items[1:])])
        if items[0] == 'result':
            result = ', '.join([f'Type.{_.upper()}' for _ in items[1:]])
    content_func_def = f'def {func_name}(self{_param}):\n    print(\'call {func_name}\')\n'
    content_func_warpper = f'{func_name}_Func = Function(store, {func_name}, FunctionType([{param}], [{result}]))'
    return content_func_def, content_func_warpper


asmLibraryArg = {
    'a': '___sys_fcntl64',
    'd': '___sys_ioctl',
    'e': '___sys_open',
    'f': '___sys_rmdir',
    'g': '___sys_unlink',
    'h': '_clock',
    'l': '_emscripten_memcpy_big',
    'm': '_emscripten_resize_heap',
    'j': '_emscripten_run_script',
    'r': '_emscripten_run_script_int',
    'q': '_emscripten_run_script_string',
    'n': '_environ_get',
    'o': '_environ_sizes_get',
    'c': '_fd_close',
    'p': '_fd_read',
    'k': '_fd_seek',
    'b': '_fd_write',
    'memory': 'wasmMemory',
    'table': 'wasmTable',
    'i': '_time'
}

namespace = 'a'

info = {
    'a': asmLibraryArg
}

path = r'iq_wasm/files/libmonalisa-v3.0.6-browser.wat'
content = Path(path).read_text(encoding='utf-8')

py_import_lines = ['from wasmer import Store, Type, Function, FunctionType, Memory\n']
func_def_lines = []
func_warpper_lines = []

for line in content.split('\n'):
    line = line.strip()
    if line.startswith('(import') is False:
        continue
    items = line.split('(')[1:]
    keys = items[0].replace('import', '').replace('"', '').strip().split(' ')
    exists_flag = True
    _tmp = info
    for index, key in enumerate(keys):
        if _tmp.get(key) is None:
            exists_flag = False
        else:
            if index == len(keys) - 1:
                func_name = _tmp[key]
                _tmp[key] += '_Func'
                _tmp = func_name
            else:
                _tmp = _tmp[key]
    if exists_flag is False:
        print(f'待导入的 {".".join(keys)} 不存在')
        continue
    contents = gen_func(_tmp, line)
    if contents is None:
        continue
    content_func_def, content_func_warpper = contents
    func_def_lines.append(content_func_def)
    func_warpper_lines.append(content_func_warpper)

func_warpper_lines = ['def gen_import_object(store: Store, memory: Memory):'] + func_warpper_lines
obj = json.dumps(info[namespace], ensure_ascii=False, indent=4)
obj = '\n'.join([f'    {_}' for _ in obj.split('\n')]).strip()
func_warpper_lines = func_warpper_lines + [f'_import_object = {obj}']
func_warpper_lines = func_warpper_lines + ['return _import_object']

content_lines = py_import_lines + func_def_lines + ['\n    '.join(func_warpper_lines)]

Path("wasm_imprt.py").write_text('\n'.join(content_lines), encoding='utf-8')