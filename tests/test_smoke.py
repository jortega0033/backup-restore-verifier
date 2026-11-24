# Scaffold smoke tests: every module imports, help and version work, the stubs exit non-zero.
import importlib
import subprocess
import sys
import unittest

MODULES = ["paths", "workspace", "contracts", "sources", "manifest",
           "restore", "compare", "store", "jobs", "server"]


def run_cli(*args):
    return subprocess.run([sys.executable, "-m", "restore_verifier", *args],
                          capture_output=True, text=True)


class ModuleImports(unittest.TestCase):
    pass


def _make(name):
    def test(self):
        importlib.import_module(f"restore_verifier.{name}")
    return test


for _name in MODULES:
    setattr(ModuleImports, f"test_import_{_name}", _make(_name))


class OracleStub(unittest.TestCase):
    def test_import_oracle(self):
        import oracle  # noqa: F401  (tests/ is the discovery top directory)


class CommandLine(unittest.TestCase):
    def test_help(self):
        r = run_cli("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("init-demo", r.stdout)

    def test_version(self):
        r = run_cli("--version")
        self.assertEqual(r.returncode, 0)
        self.assertIn("0.0.0", r.stdout)

    def test_stub_exits_non_zero(self):
        for command in ("init-demo", "serve"):
            with self.subTest(command=command):
                r = run_cli("--workspace", ".restore-verifier", command)
                self.assertNotEqual(r.returncode, 0)
                self.assertIn("not implemented yet: see #2", r.stderr)


if __name__ == "__main__":
    unittest.main()
