from pathlib import Path
from wasmer_compiler_cranelift import Compiler
from wasmer import wat2wasm, engine, Store, Module, Memory, MemoryType

from iq_wasm.wasm_helper import Instance


wasm = wat2wasm(Path(r'iq_wasm/files/libmonalisa-v3.0.6-browser.wat').read_text(encoding='utf-8'))
# wasm = Path(r'iq_wasm/files/libmonalisa-v3.0.6-browser.wasm').read_bytes()
# 初始化一个存储器
store = Store(engine.JIT(Compiler))
# 载入wasm
module = Module(store, wasm)
# 构建一个线性内存
memory = Memory(store, MemoryType(256, 256, shared=False))
# 初始化实例 内存+模块+外部导入函数
instance = Instance(memory, module, store)
instance.run()