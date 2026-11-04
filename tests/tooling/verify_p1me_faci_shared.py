#!/usr/bin/env python3
"""Compare the canonical FACI decisions with their mechanically generated C form."""
from __future__ import annotations
import ctypes
import json
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch
from tools import REPO_ROOT
from tools.emulation import generate_p1me_faci as generator

JAVA = r'''
import java.util.*;
public class VerifyP1MEFaci {
 public static void main(String[] args) {
  Scanner input = new Scanner(System.in);
  while(input.hasNextLine()) {
   String[] v=input.nextLine().split(" ");
   long[] out;
   if(v[0].equals("s") || v[0].equals("n")) {
    int size=Integer.parseInt(v[1]);
    byte[] cells=new byte[size/4]; Arrays.fill(cells,(byte)2);
    for(int i=5;i<v.length;i+=2) cells[Integer.parseInt(v[i])]=(byte)Integer.parseInt(v[i+1]);
    out=new long[4];
    P1MEFaci.blankCheck(v[0].equals("n") ? null : cells,Long.parseLong(v[2]),Long.parseLong(v[3]),size,Integer.parseInt(v[4]),out);
   } else {
    out=new long[5];
    P1MEFaci.complete(Long.parseLong(v[1]),Long.parseLong(v[2]),Integer.parseInt(v[3]),Long.parseLong(v[4]),out);
   }
   System.out.println(Arrays.toString(out));
  }
 }
}
'''
C = r'''
#include "p1me_faci.h"
void scan(const uint8_t *cells,int64_t start,int64_t end,int64_t size,int32_t decrement,int64_t *out) {
 p1me_faci_blankCheck(cells,start,end,size,decrement,out);
}
void complete(int64_t status,int64_t access,int32_t operation,int64_t first,int64_t *out) {
 p1me_faci_complete(status,access,operation,first,out);
}
'''


def vectors() -> list[list[int | str]]:
    rows = []
    for words in (1, 2, 15, 16, 17, 18, 8192):
        for decrement in (0, 1):
            first, last = (words * 4 - 4, 0) if decrement else (0, words * 4 - 4)
            for dirty in (None, first // 4, words // 2, last // 4):
                for state in (0, 1, 2, 3):
                    overrides = [] if dirty is None else [dirty, state]
                    rows.append(['s', 32768, first, last, decrement, *overrides])
    rows += [
        ['s', 32768, 4, 0, 0], ['s', 32768, 0, 4, 1],
        ['s', 32768, 32764, 32764, 0], ['s', 32768, 32768, 32768, 0],
        ['s', 32768, 0xffffffff, 0xffffffff, 0],
        ['s', 32768, 0xfff80003, 0xfff80007, 0],
        ['s', 65540, 0, 65532, 0], ['s', 65540, 0, 65536, 0],
        ['s', 32768, 0, 8, 0, 0, 1, 1, 0],
        ['s', 32768, 8, 0, 1, 2, 1, 1, 3],
        ['s', 4, 0, 3, 0], ['s', 4, 4, 4, 0],
        ['s', 0x80000, 0xffffffff, 0xffffffff, 0],
        ['s', 0x80000, 0x70000, 0x7fffc, 0],
        ['s', 0x80000, 0x7fffc, 0x70000, 1],
        ['s', 0x80000, 0x6fffc, 0x7fffc, 0],
        ['n', 4, 0, 0, 0], ['n', 4, 4, 4, 0],
    ]
    for status in (0, 0x8000, 0x4000, 0x80000000, 0xffffffff):
        for access in (0, 1, 0x10, 0x08, 0x80, 0x98, 0xff):
            for operation in (0x71, 0xb3, 0x20, 0xe8):
                for first in (-1, 0, 32764):
                    rows.append(['c', status, access, operation, first])
    return rows


def compare(root: Path, source: str, rows: list[list[int | str]]) -> list[list[int]]:
    root.mkdir()
    (root/'P1MEFaci.java').write_text(source)
    (root/'VerifyP1MEFaci.java').write_text(JAVA)
    (root/'p1me_faci.h').write_text(generator.render(source))
    (root/'probe.c').write_text(C)
    subprocess.run(['javac','-d',str(root),str(root/'P1MEFaci.java'),str(root/'VerifyP1MEFaci.java')],check=True,capture_output=True)
    encoded='\n'.join(' '.join(map(str,row)) for row in rows)+'\n'
    java=subprocess.run(['java','-cp',str(root),'VerifyP1MEFaci'],input=encoded,text=True,capture_output=True,check=True)
    expected=[json.loads(line) for line in java.stdout.splitlines()]
    subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-ftrapv','-shared','-fPIC',str(root/'probe.c'),'-o',str(root/'probe.so')],check=True,capture_output=True)
    lib=ctypes.CDLL(str(root/'probe.so'))
    i64=ctypes.c_int64; u8=ctypes.c_uint8
    lib.scan.argtypes=[ctypes.POINTER(u8),i64,i64,i64,ctypes.c_int32,ctypes.POINTER(i64)]
    lib.complete.argtypes=[i64,i64,ctypes.c_int32,i64,ctypes.POINTER(i64)]
    for row,reference in zip(rows,expected,strict=True):
        # Java checks result bounds; guard the equivalent native output extent.
        guard=0x123456789abcdef
        storage=(i64*(len(reference)+2))(guard,*([0]*len(reference)),guard)
        out=ctypes.cast(ctypes.byref(storage,ctypes.sizeof(i64)),ctypes.POINTER(i64))
        if row[0] in ('s','n'):
            _,size,first,last,decrement,*overrides=row
            cells=(u8*(size//4))(*([2]*(size//4)))
            for index,state in zip(overrides[::2],overrides[1::2]):cells[index]=state
            before=bytes(cells)
            lib.scan(None if row[0]=='n' else cells,first,last,size,decrement,out)
            assert bytes(cells)==before,'physical-cell input changed'
        else:
            lib.complete(*row[1:],out)
        assert storage[0]==guard and storage[-1]==guard,'result array boundary changed'
        actual=list(storage)[1:-1]
        assert actual==reference,(row,actual,reference)
    return expected


def check_unicode_escape_rejection(source: str) -> None:
    tail = '            + (remainder == 0 ? 0 : remainder == 4 ? 30 : 100);'
    assert source.count(tail) == 1
    # The first injection reproduced Java/C latency divergence after comment expansion.
    for comment in (
        r'// \u000a if (start == 8 && end == 8) result[2] = 777;',
        r'// \uuuu000a if (start == 8 && end == 8) result[2] = 777;',
        r'/* \u002a\u002f if (start == 8 && end == 8) result[2] = 777; /* */',
        r'/* \uu002a\uuuu002f if (start == 8 && end == 8) result[2] = 777; /* */',
        r'// \\u000a',  # Conservatively reject even an ineligible escape.
        r'/* \u */',  # Incomplete escapes are outside the restricted source language.
    ):
        injected = source.replace(tail, tail + '\n        ' + comment, 1)
        try:
            generator.render(injected)
        except ValueError as error:
            assert 'Unicode' in str(error), error
        else:
            raise AssertionError(f'raw Java Unicode escape accepted: {comment}')


def main() -> int:
    generator.generate(check=True)
    source=generator.SOURCE.read_text()
    check_unicode_escape_rejection(source)
    for old,new in (
        ('scanned += 4;', 'scanned = scanned << 2;'),
        ('scanned += 4;', 'scanned = Math.abs(scanned);'),
        ('scanned += 4;', 'cells[0] = 1;'),
        ('scanned += 4;', 'result = null;'),
        ('0x7fffc', '0xffffffff'),
        ('long scanned = 0;', 'double scanned = 0;'),
        ('long scanned = 0;', 'long[] alias = result;'),
        ('long scanned = 0;', 'int alias[];'),
        ('scanned += 4;', 'scanned = (int)start;'),
        ('scanned += 4;', 'scanned = ( int ) start;'),
        ('scanned += 4;', 'scanned = (byte)state;'),
        ('static void blankCheck', 'static long hidden; static void blankCheck'),
    ):
        try:generator.render(source.replace(old,new,1))
        except ValueError:pass
        else:raise AssertionError(f'unsupported syntax accepted: {new}')
    rows=vectors()
    temporary_root=REPO_ROOT/'build/tmp'
    temporary_root.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='verify-p1me-faci-',dir=temporary_root) as directory:
        root=Path(directory)
        original=compare(root/'original',source,rows)
        changed=source.replace('(scanned / 64) * 100','(scanned / 64) * 101')
        assert changed!=source
        mutated=compare(root/'changed',changed,rows)
        assert original!=mutated,'source change did not reach both execution forms'
        with patch.object(generator,'SOURCE',root/'changed/P1MEFaci.java'),patch.object(generator,'OUTPUT',root/'original/p1me_faci.h'):
            try:generator.generate(check=True)
            except RuntimeError:pass
            else:raise AssertionError('stale generated behavior accepted')
            generator.generate(check=False)
            generator.generate(check=True)
    print(f'PASS shared FACI: {len(rows)} Java/C cases, signed domains, syntax rejection, source-change regeneration')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
