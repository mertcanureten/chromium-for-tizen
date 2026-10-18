"""Use V8's portable switch dispatch for the NaCl RegExp interpreter.

The computed-label dispatch path hangs on /a+/u.test('aaa') on the target TV.
Keep the interpreter and all matching semantics; use its existing switch path.
"""
from pathlib import Path
p=Path('/work/v8/src/regexp/regexp-interpreter.cc');s=p.read_text()
old='#if V8_HAS_COMPUTED_GOTO && \\'
new='#if !defined(__native_client__) && V8_HAS_COMPUTED_GOTO && \\'
if new not in s:
 assert old in s;s=s.replace(old,new,1);p.write_text(s)
