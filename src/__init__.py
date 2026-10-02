"""Educational Performance Analytics Package"""

# NumPy 2.0 backward compatibility shim for older installed scientific libraries
import numpy as np

for _attr, _target in [
    ("round_", np.round),
    ("unicode_", np.str_),
    ("bytes_", bytes),
    ("string_", bytes),
    ("bool_", bool),
    ("int_", int),
    ("float_", float)
]:
    if not hasattr(np, _attr):
        setattr(np, _attr, _target)
