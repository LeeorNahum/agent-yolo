"""Windows integration matrix. Python is needed only for testing, not launching."""
import argparse
import base64
import csv
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
WRAPPERS = list(csv.DictReader((ROOT / "wrappers.csv").open()))
PARSER = argparse.ArgumentParser()
PARSER.add_argument("--installed", action="store_true")
PARSER.add_argument("--unc", help="Existing writable UNC directory for additional native tests")
OPTIONS, REST = PARSER.parse_known_args()


class ShellExecuteInfo(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.DWORD), ("fMask", wintypes.ULONG),
                ("hwnd", wintypes.HWND), ("lpVerb", wintypes.LPCWSTR),
                ("lpFile", wintypes.LPCWSTR), ("lpParameters", wintypes.LPCWSTR),
                ("lpDirectory", wintypes.LPCWSTR), ("nShow", ctypes.c_int),
                ("hInstApp", wintypes.HINSTANCE), ("lpIDList", ctypes.c_void_p),
                ("lpClass", wintypes.LPCWSTR), ("hkeyClass", wintypes.HKEY),
                ("dwHotKey", wintypes.DWORD), ("hIcon", wintypes.HANDLE),
                ("hProcess", wintypes.HANDLE)]


def shell_execute(executable, raw, cwd):
    """Explorer-equivalent ShellExecuteEx, including App Paths resolution."""
    shell = ctypes.WinDLL("shell32", use_last_error=True)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    shell.ShellExecuteExW.argtypes = [ctypes.POINTER(ShellExecuteInfo)]
    shell.ShellExecuteExW.restype = wintypes.BOOL
    kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    info = ShellExecuteInfo()
    info.cbSize = ctypes.sizeof(info)
    info.fMask = 0x40 | 0x100 | 0x400  # process handle, synchronous launch, no error UI
    info.lpFile, info.lpParameters, info.lpDirectory = str(executable), raw, str(cwd)
    info.nShow = 0  # Hidden test child, never open agent UI.
    if not shell.ShellExecuteExW(ctypes.byref(info)):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        if kernel.WaitForSingleObject(info.hProcess, 15000) != 0:
            raise TimeoutError("ShellExecute child did not exit")
        code = wintypes.DWORD()
        if not kernel.GetExitCodeProcess(info.hProcess, ctypes.byref(code)):
            raise ctypes.WinError(ctypes.get_last_error())
        return code.value
    finally:
        kernel.CloseHandle(info.hProcess)


class WindowsLaunchers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="agent-yolo é ")
        cls.base = Path(cls.temp.name)
        cls.bin = cls.base / "install & ! % space 日本"
        cls.cwd = cls.base / "work & ! % é 日本"
        cls.targets = cls.base / "CLI space é"
        for directory in (cls.bin, cls.cwd, cls.targets):
            directory.mkdir()
        cls.capture = cls.base / "capture.txt"
        cls.original_env = os.environ.copy()
        cls.powershell = shutil.which("powershell.exe")
        cls.pwsh = shutil.which("pwsh.exe")
        compiler = Path(os.environ["SystemRoot"]) / "Microsoft.NET/Framework64/v4.0.30319/csc.exe"
        if not compiler.exists():
            compiler = Path(os.environ["SystemRoot"]) / "Microsoft.NET/Framework/v4.0.30319/csc.exe"
        subprocess.run([str(compiler), "/nologo", "/warnaserror+", "/out:" + str(cls.targets / "probe.exe"), str(ROOT / "tests/probe.cs")], check=True)
        for wrapper in WRAPPERS:
            name = wrapper["Name"]
            shutil.copy2(cls.targets / "probe.exe", cls.targets / (wrapper["Command"] + ".exe"))
            source = Path(os.environ["USERPROFILE"]) / ".local/bin" if OPTIONS.installed else ROOT / "dist"
            shutil.copy2(source / (name + ".exe"), cls.bin / (name + ".exe"))
            shutil.copy2(ROOT / name / (name + ".cmd"), cls.bin / (name + ".cmd"))
        os.environ["PATH"] = str(cls.targets) + ";" + str(cls.bin)
        os.environ["AGENT_YOLO_CAPTURE"] = str(cls.capture)
        os.environ["YOLO_EXPAND"] = "EXPANDED"
        cls.evidence = []

    @classmethod
    def tearDownClass(cls):
        os.environ.clear()
        os.environ.update(cls.original_env)
        (ROOT / "dist" / ("installed-tests.json" if OPTIONS.installed else "tests.json")).write_text(json.dumps(cls.evidence, ensure_ascii=False, indent=2), encoding="utf-8")
        cls.temp.cleanup()

    def check_capture(self, wrapper, expected, cwd, label, code):
        self.assertEqual(code, 37, label)
        lines = self.capture.read_text(encoding="ascii").splitlines()
        values = [base64.b64decode(line).decode("utf-16-le") for line in lines]
        self.assertEqual(values[0], str(cwd), label)
        self.assertEqual(values[2:], [wrapper["Permission"], *expected], label)
        self.evidence.append(dict(wrapper=wrapper["Name"], case=label, cwd=values[0], argv=values[2:], raw=values[1], exit=code))
        self.capture.unlink()

    def assert_crlf(self, path, fix):
        rest = path.read_bytes().replace(b"\r\n", b"")
        self.assertFalse(b"\r" in rest or b"\n" in rest, path.name + " has a line ending other than CRLF. " + fix)

    def run_native(self, wrapper, args, shell=False, cwd=None):
        cwd = cwd or self.cwd
        exe = self.bin / (wrapper["Name"] + ".exe")
        raw = subprocess.list2cmdline(args)
        if shell:
            code = shell_execute(exe, raw, cwd)
        else:
            code = subprocess.run([str(exe), *args], cwd=cwd, capture_output=True, timeout=15).returncode
        self.check_capture(wrapper, args, cwd, "ShellExecute" if shell else "CreateProcess", code)

    def test_native_matrix(self):
        cases = [[], [""], ["first", "", "third", ""],
                 ["two words", "é日本", "--model", "explicit-model", "--", "-option"],
                 ['a"b', 'slash\\"quote', "ends with slash\\", "\\\\server\\share\\"],
                 ["a&b|c<d>e^f", "%YOLO_EXPAND%", "!YOLO_EXPAND!", "(group)", "`$x;*?"],
                 ["tab\there", "line\nfeed", "vertical\vtab", "carriage\rreturn"],
                 ["x" * 8192, "tail"]]
        for wrapper in WRAPPERS:
            for args in cases:
                for shell in (False, True):
                    with self.subTest(wrapper=wrapper["Name"], args=args, shell=shell):
                        self.run_native(wrapper, args, shell)

    def test_cmd_contract(self):
        args = ["two words", "", "--option", "é日本", "a&b|c<d>e^f", "!literal!", "tail\\"]
        # cmd quotes protect metacharacters. Percent and delayed expansion belong to cmd.
        raw = '"two words" "" --option é日本 "a&b|c<d>e^f" "!literal!" tail\\'
        for wrapper in WRAPPERS:
            for extension in ("", ".exe", ".cmd"):
                command = wrapper["Name"] + extension + " " + raw
                result = subprocess.run('"' + os.environ["COMSPEC"] + '" /d /v:off /s /c "' + command + '"', cwd=self.cwd, capture_output=True, timeout=15)
                self.check_capture(wrapper, args, self.cwd, "cmd " + extension, result.returncode)

    def test_powershell_contract(self):
        for shell in (self.powershell, self.pwsh):
            if not shell:
                continue
            modern = shell == self.pwsh
            args = ["two words", "--option", "é日本", "a&b|c<d>e^f", "%YOLO_EXPAND%", "!literal!", "tail\\"]
            if modern:
                args += ["", 'a"b']
            for wrapper in WRAPPERS:
                script = ("$PSNativeCommandArgumentPassing = 'Standard'; " if modern else "") + wrapper["Name"] + " " + " ".join("'" + a.replace("'", "''") + "'" for a in args) + "; exit $LASTEXITCODE"
                encoded = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
                result = subprocess.run([shell, "-NoProfile", "-EncodedCommand", encoded], cwd=self.cwd, capture_output=True, timeout=15)
                self.check_capture(wrapper, args, self.cwd, "PowerShell " + ("7" if modern else "5.1"), result.returncode)

    def test_cmd_expansion_belongs_to_caller(self):
        os.environ["YOLO_NESTED"] = "%YOLO_EXPAND%"
        for wrapper in WRAPPERS:
            command = wrapper["Name"] + ' "%YOLO_NESTED%" "!YOLO_EXPAND!" a^&b'
            result = subprocess.run('"' + os.environ["COMSPEC"] + '" /d /v:on /s /c "' + command + '"', cwd=self.cwd, capture_output=True, timeout=15)
            self.check_capture(wrapper, ["%YOLO_EXPAND%", "EXPANDED", "a&b"], self.cwd, "cmd single expansion", result.returncode)

    def test_quoted_absolute_path_after_relative_decoy(self):
        previous = os.environ["PATH"]
        try:
            os.environ["PATH"] = '.;C:relative;\\relative;"' + str(self.targets) + '"'
            for wrapper in WRAPPERS:
                self.run_native(wrapper, ["PATH", ""])
        finally:
            os.environ["PATH"] = previous

    def test_batch_only_and_relative_path_rejected(self):
        original_path = os.environ["PATH"]
        try:
            os.environ["PATH"] = ".;C:relative;\\relative;"
            for wrapper in WRAPPERS:
                shutil.copy2(self.targets / "probe.exe", self.cwd / (wrapper["Command"] + ".exe"))
                (self.cwd / (wrapper["Command"] + ".cmd")).write_text("@echo should-never-run\n")
                result = subprocess.run([str(self.bin / (wrapper["Name"] + ".exe"))], cwd=self.cwd, capture_output=True, timeout=15)
                self.assertEqual(result.returncode, 9009)
                self.assertIn(b"native CLI", result.stderr)
                self.assertFalse(self.capture.exists())
        finally:
            os.environ["PATH"] = original_path

    def test_raw_tail_matches_direct_cli(self):
        # Compare actual runtime argv, including unusual but legal Windows quoting.
        tails = [' "" "a""b"', '\talpha\t"two words"', ' "unterminated value',
                 ' "a\\\\\\"b" "end\\\\"', ' %YOLO_EXPAND% !YOLO_EXPAND! &|<>^',
                 ' "\u00e9\u65e5\u672c" "" --model user-choice -- --prompt']
        for wrapper in WRAPPERS:
            exe = self.bin / (wrapper["Name"] + ".exe")
            for tail in tails:
                direct = '"' + str(self.targets / (wrapper["Command"] + ".exe")) + '" ' + wrapper["Permission"] + tail
                subprocess.run(direct, cwd=self.cwd, capture_output=True, timeout=15)
                expected = [base64.b64decode(line).decode("utf-16-le") for line in self.capture.read_text().splitlines()][2:]
                self.capture.unlink()
                # Partially quoted argv[0] must also be skipped correctly.
                command = '"' + str(self.bin) + '"\\' + wrapper["Name"] + '.exe' + tail
                result = subprocess.run(command, executable=str(exe), cwd=self.cwd, capture_output=True, timeout=15)
                self.check_capture(wrapper, expected[1:], self.cwd, "raw tail oracle", result.returncode)

    def test_renamed_launcher_does_not_recurse(self):
        for wrapper in WRAPPERS:
            renamed = self.cwd / (wrapper["Command"] + ".exe")
            shutil.copy2(self.bin / (wrapper["Name"] + ".exe"), renamed)
            result = subprocess.run([str(renamed)], cwd=self.cwd, capture_output=True, timeout=15)
            self.assertEqual(result.returncode, 9009)
            self.assertIn(b"recursion", result.stderr)

    def test_manifest_and_wrapper_drift(self):
        self.assertEqual({w["Name"] for w in WRAPPERS}, {p.parent.name for p in ROOT.glob("*/*.sh")})
        for wrapper in WRAPPERS:
            name = wrapper["Name"]
            self.assertEqual((ROOT / name / (name + ".sh")).read_text().splitlines(),
                             ["#!/bin/sh", 'exec ' + wrapper["Command"] + ' ' + wrapper["Permission"] + ' "$@"'])
            # .gitattributes pins these endings. A mismatch means a stale checkout or an editor that changed them.
            restore = ", or, if it has no local edits, delete it and restore it with git checkout."
            self.assert_crlf(ROOT / name / (name + ".cmd"), "Save it with CRLF endings" + restore)
            self.assertNotIn(b"\r", (ROOT / name / (name + ".sh")).read_bytes(), name + ".sh contains CR. Save it with LF endings" + restore)
            cmd = (ROOT / name / (name + ".cmd")).read_text()
            self.assertNotIn("call ", cmd.lower())
            self.assertNotIn("--", cmd)
            self.assertEqual(cmd.count("%*"), 2)

    def test_build_in_nonstandard_checkout(self):
        checkout = self.base / "checkout & % ! 日本"
        checkout.mkdir()
        for filename in ("build.ps1", "VERSION", "launcher.cs", "wrappers.csv"):
            shutil.copy2(ROOT / filename, checkout / filename)
        result = subprocess.run([self.powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(checkout / "build.ps1")], cwd=self.cwd, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        for wrapper in WRAPPERS:
            self.assertTrue((checkout / "dist" / (wrapper["Name"] + ".exe")).is_file())

    def test_legacy_regression_evidence(self):
        # Reproduce the previous two-layer installation without touching installed files.
        legacy = self.base / "legacy"
        legacy.mkdir()
        inner = legacy / "inner.cmd"
        outer = legacy / "outer.cmd"
        inner.write_text('@echo off\ncodex --dangerously-bypass-approvals-and-sandbox %*\n')
        os.environ["YOLO_LEGACY_INNER"] = str(inner)
        outer.write_text('@echo off\ncall "%YOLO_LEGACY_INNER%" %*\n')
        for cwd in [self.cwd] + ([Path(OPTIONS.unc)] if OPTIONS.unc else []):
            shell_execute(outer, '"%YOLO_EXPAND%" "two words"', cwd)
            values = [base64.b64decode(line).decode("utf-16-le") for line in self.capture.read_text().splitlines()]
            self.evidence.append(dict(wrapper="legacy", case="ShellExecute batch regression", requested_cwd=str(cwd), cwd=values[0], argv=values[2:]))
            self.assertNotEqual(values[2:], ["--dangerously-bypass-approvals-and-sandbox", "%YOLO_EXPAND%", "two words"])
            self.capture.unlink()

    @unittest.skipUnless(OPTIONS.installed, "Requires installed App Paths entries")
    def test_installed_app_paths(self):
        for wrapper in WRAPPERS:
            for suffix in ("", ".exe"):
                args = ["", "two words", "%YOLO_EXPAND%", "!literal!", "a&b|c", 'é"x']
                # Remove the copied wrappers from PATH, forcing registered-name resolution.
                previous = os.environ["PATH"]
                try:
                    os.environ["PATH"] = str(self.targets)
                    code = shell_execute(wrapper["Name"] + suffix, subprocess.list2cmdline(args), self.cwd)
                finally:
                    os.environ["PATH"] = previous
                self.check_capture(wrapper, args, self.cwd, "installed App Paths " + suffix, code)

    @unittest.skipUnless(OPTIONS.installed, "Requires installed shims")
    def test_installed_shim_endings(self):
        local = Path(os.environ["USERPROFILE"]) / ".local"
        for wrapper in WRAPPERS:
            name = wrapper["Name"]
            for shim in (local / "bin" / (name + ".cmd"), local / "share/agent-yolo" / name / (name + ".cmd")):
                if shim.exists():
                    self.assert_crlf(shim, "Fix this checkout's launcher endings, then rerun install.ps1.")

    @unittest.skipUnless(OPTIONS.unc, "Use --unc with a reachable UNC directory")
    def test_unc(self):
        for wrapper in WRAPPERS:
            for shell in (False, True):
                self.run_native(wrapper, ["", "UNC & % ! é"], shell, Path(OPTIONS.unc))


if __name__ == "__main__":
    unittest.main(argv=[__file__, *REST], verbosity=2)
