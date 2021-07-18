import sys
from wasmer import Store, Type, Function, FunctionType, Memory, Module, ImportObject

from wasmer import Instance as WasmerInstance


class Instance:

    def __init__(self, memory: Memory, module: Module, store: Store):
        DYNAMIC_BASE = 6065008
        DYNAMICTOP_PTR = 821968
        # 预先的内存操作
        memory.int32_view()[DYNAMICTOP_PTR >> 2] = DYNAMIC_BASE
        # 构建env 即外部导入函数
        _import_object = self.gen_import_object(store, memory=memory)
        # 初始化env并注册外部导入函数 -> register('env', {'key': func, ...})
        self.import_object = ImportObject()
        self.import_object.register('a', _import_object)
        self.asm = WasmerInstance(module, import_object=self.import_object)
        self.exports = self.asm.exports
        self.memory = memory
        self.stack = 0
        self._ctx = None # type: int
        self.export_configs = {
            '___wasm_call_ctors': self.exports.s,
            '_monalisa_context_alloc': self.exports.D,
            'monalisa_set_license': self.exports.F,
            '_monalisa_set_canvas_id': self.exports.t,
            '_monalisa_version_get': self.exports.A,
            'monalisa_get_line_number': self.exports.v,
            'stackAlloc': self.exports.N,
            'stackSave': self.exports.L,
            'stackRestore': self.exports.M,
        }

    def run(self):
        self.doinit()
        self._moSetLicense()
        self._moSetCanvasId()
        self._moGetVersion()
        self.get_line_number()

    def doinit(self):
        self.___wasm_call_ctors()
        self._ctx = self._monalisa_context_alloc()

    def _moSetLicense(self):
        license = 'AIUACgMAAAAAAAAAAAQChgACATADhwAnAgAg3UBbUdVCWXAjkgoUgmICmHvomvZai0jGglWe+oaQC+MCAAAAA4gANwEAMHStDt3ZksUi3Q7ZpevUL0ce2NA73SNiqOJW3Wc0P6B62xYg8yiWFF92KXEGjljOeQEAAgD/iQAkAQAAIKgivL0LDGFSYlwcToEO6LCRYFZjE3lycoiZDPxiNXFo'
        ret = self.ccall('monalisa_set_license', int, self._ctx, license, len(license), '0')
        print('_moSetLicense', ret)
        with open('iq_wasm/files/mem.bin', 'wb') as f:
            mem = bytes(self.memory.uint8_view()[:])
            f.write(mem)
            print(mem[0x5C8C0C:0x5C8C0C + 16].hex())

    def _moSetCanvasId(self):
        _canvasId = 'subtitlesubtitle'
        ret = self.ccall('_monalisa_set_canvas_id', int, self._ctx, _canvasId, len(_canvasId))
        print('_moSetCanvasId', ret)

    def _moGetVersion(self):
        ret = self.export_configs['_monalisa_version_get']()
        print('_moGetVersion', ret)

    def get_line_number(self):
        enc_text = 'F6vjGQAlaXWf/rYLFkGHQLok+aI/X+7MBJI6EmzYtZ4='
        ret = self.ccall('monalisa_get_line_number', int, self._ctx, enc_text, len(enc_text), '(?:<br\\/>|\\n)')
        print('get_line_number', ret)

    def ___wasm_call_ctors(self):
        func_name = sys._getframe().f_code.co_name
        return self.export_configs[func_name]()

    def _monalisa_context_alloc(self):
        func_name = sys._getframe().f_code.co_name
        return self.export_configs[func_name]()

    def stackAlloc(self, length: int):
        func_name = sys._getframe().f_code.co_name
        return self.export_configs[func_name](length)

    def stackSave(self):
        func_name = sys._getframe().f_code.co_name
        return self.export_configs[func_name]()

    def stackRestore(self, stack: int):
        func_name = sys._getframe().f_code.co_name
        return self.export_configs[func_name](stack)

    def stringToUTF8(self, data: str, ptr: int, max_write_length: int):
        _data = data.encode('utf-8')
        write_length = len(_data)
        if write_length == 0:
            self.memory.uint8_view()[ptr] = 0
        elif write_length > max_write_length:
            write_length = max_write_length
            self.memory.uint8_view()[ptr:ptr + write_length] = _data[:write_length]
        else:
            self.memory.uint8_view()[ptr:ptr + write_length] = _data
        return write_length

    def writeArrayToMemory(self, array: list, ptr: int):
        self.memory.int8_view()[ptr:ptr + len(array)] = array

    def UTF8ToString(self, ptr: int) -> str:
        if ptr > 0:
            _memory = self.memory.uint8_view(offset=ptr)
            data = []
            index = 0
            while(_memory[index] != 0):
                data.append(_memory[index])
                index += 1
            return bytes(data).decode('utf-8')
        else:
            return ''

    def ccall(self, func_name: str, returnType: 'type', *args):
        def convertReturnValue(_ptr: int):
            if returnType == str:
                return self.UTF8ToString(_ptr)
            elif returnType == bool:
                return bool(returnType)
            return _ptr
        stack = 0
        _args = []
        for arg in args:
            if isinstance(arg, str):
                if stack == 0:
                    stack = self.stackSave()
                max_write_length = (len(arg) << 2) + 1
                ptr = self.stackAlloc(max_write_length)
                self.stringToUTF8(arg, ptr, max_write_length)
                _args.append(ptr)
            elif isinstance(arg, list):
                ptr = self.stackAlloc(len(arg))
                ptr = self.writeArrayToMemory(arg, ptr)
                _args.append(ptr)
            else:
                _args.append(arg)
        ptr = self.export_configs[func_name](*_args)
        ret = convertReturnValue(ptr)
        if stack != 0:
            self.stackRestore(stack)
        return ret

    def ___sys_fcntl64(self, param_0, param_1, param_2):
        print('call ___sys_fcntl64')

    def _fd_write(self, param_0, param_1, param_2, param_3):
        print('call _fd_write')

    def _fd_close(self, param_0):
        print('call _fd_close')

    def ___sys_ioctl(self, param_0, param_1, param_2):
        print('call ___sys_ioctl')

    def ___sys_open(self, param_0, param_1, param_2):
        print('call ___sys_open')

    def ___sys_rmdir(self, param_0):
        print('call ___sys_rmdir')

    def ___sys_unlink(self, param_0):
        print('call ___sys_unlink')

    def _clock(self):
        print('call _clock')

    def _time(self, param_0):
        print('call _time')

    def _emscripten_run_script(self, param_0):
        print('call _emscripten_run_script')

    def _fd_seek(self, param_0, param_1, param_2, param_3, param_4):
        print('call _fd_seek')

    def _emscripten_memcpy_big(self, dest: int, src: int, num: int = None):
        # print('call _emscripten_memcpy_big', dest, src, num)
        if num is None:
            num = len(self.memory.uint8_view()) - 1
        self.memory.uint8_view()[dest:dest + num] = self.memory.uint8_view()[src:src + num]
        return dest

    def _emscripten_resize_heap(self, param_0):
        print('call _emscripten_resize_heap')

    def _environ_get(self, __environ, environ_buf):
        print('call _environ_get', __environ, environ_buf)
        bufSize = 0
        strings = self.getEnvStrings()
        for index, string in enumerate(strings):
            ptr = environ_buf + bufSize
            self.memory.int32_view()[__environ + index * 4 >> 2] = ptr
            self.writeAsciiToMemory(string, ptr)
            bufSize += len(string) + 1
        return 0

    def writeAsciiToMemory(self, string, buffer, dontAddNull: int = 0):
        for num in list(string.encode('utf-8')):
            self.memory.int8_view()[buffer >> 0] = num
            buffer += 1
        if dontAddNull == 0:
            self.memory.int8_view()[buffer >> 0] = 0

    def getEnvStrings(self):
        return ['USER=web_user', 'LOGNAME=web_user', 'PATH=/', 'PWD=/', 'HOME=/home/web_user', 'LANG=zh_CN.UTF-8', '_=./this.program']

    def _environ_sizes_get(self, penviron_count: int, penviron_buf_size: int):
        print('call _environ_sizes_get', penviron_count, penviron_buf_size)
        strings = self.getEnvStrings()
        self.memory.int32_view()[penviron_count >> 2] = len(strings)
        bufSize = 0
        for string in strings:
            bufSize += len(string) + 1
        self.memory.int32_view()[penviron_buf_size >> 2] = bufSize
        return 0

    def _fd_read(self, param_0, param_1, param_2, param_3):
        print('call _fd_read')

    def _emscripten_run_script_string(self, param_0):
        print('call _emscripten_run_script_string')

    def _emscripten_run_script_int(self, param_0):
        text = self.UTF8ToString(param_0)
        # 原函数这里是运行一段js代码 这里是python 所以运行不了
        # 按执行对应的结果给返回即可 必须这里是根据<br>返回字幕行数的
        # eval(text)
        print('call _emscripten_run_script_int', text)
        return 1

    def gen_import_object(self, store: Store, memory: Memory):
        ___sys_fcntl64_Func = Function(store, self.___sys_fcntl64, FunctionType([Type.I32, Type.I32, Type.I32], [Type.I32]))
        _fd_write_Func = Function(store, self._fd_write, FunctionType([Type.I32, Type.I32, Type.I32, Type.I32], [Type.I32]))
        _fd_close_Func = Function(store, self._fd_close, FunctionType([Type.I32], [Type.I32]))
        ___sys_ioctl_Func = Function(store, self.___sys_ioctl, FunctionType([Type.I32, Type.I32, Type.I32], [Type.I32]))
        ___sys_open_Func = Function(store, self.___sys_open, FunctionType([Type.I32, Type.I32, Type.I32], [Type.I32]))
        ___sys_rmdir_Func = Function(store, self.___sys_rmdir, FunctionType([Type.I32], [Type.I32]))
        ___sys_unlink_Func = Function(store, self.___sys_unlink, FunctionType([Type.I32], [Type.I32]))
        _clock_Func = Function(store, self._clock, FunctionType([], [Type.I32]))
        _time_Func = Function(store, self._time, FunctionType([Type.I32], [Type.I32]))
        _emscripten_run_script_Func = Function(store, self._emscripten_run_script, FunctionType([Type.I32], []))
        _fd_seek_Func = Function(store, self._fd_seek, FunctionType([Type.I32, Type.I32, Type.I32, Type.I32, Type.I32], [Type.I32]))
        _emscripten_memcpy_big_Func = Function(store, self._emscripten_memcpy_big, FunctionType([Type.I32, Type.I32, Type.I32], [Type.I32]))
        _emscripten_resize_heap_Func = Function(store, self._emscripten_resize_heap, FunctionType([Type.I32], [Type.I32]))
        _environ_get_Func = Function(store, self._environ_get, FunctionType([Type.I32, Type.I32], [Type.I32]))
        _environ_sizes_get_Func = Function(store, self._environ_sizes_get, FunctionType([Type.I32, Type.I32], [Type.I32]))
        _fd_read_Func = Function(store, self._fd_read, FunctionType([Type.I32, Type.I32, Type.I32, Type.I32], [Type.I32]))
        _emscripten_run_script_string_Func = Function(store, self._emscripten_run_script_string, FunctionType([Type.I32], [Type.I32]))
        _emscripten_run_script_int_Func = Function(store, self._emscripten_run_script_int, FunctionType([Type.I32], [Type.I32]))
        # wasmMemory_Func = Function(store, wasmMemory, FunctionType([], []))
        _import_object = {
            "a": ___sys_fcntl64_Func,
            "d": ___sys_ioctl_Func,
            "e": ___sys_open_Func,
            "f": ___sys_rmdir_Func,
            "g": ___sys_unlink_Func,
            "h": _clock_Func,
            "l": _emscripten_memcpy_big_Func,
            "m": _emscripten_resize_heap_Func,
            "j": _emscripten_run_script_Func,
            "r": _emscripten_run_script_int_Func,
            "q": _emscripten_run_script_string_Func,
            "n": _environ_get_Func,
            "o": _environ_sizes_get_Func,
            "c": _fd_close_Func,
            "p": _fd_read_Func,
            "k": _fd_seek_Func,
            "b": _fd_write_Func,
            "memory": memory,
            # "table": wasmTable,
            "i": _time_Func
        }
        return _import_object