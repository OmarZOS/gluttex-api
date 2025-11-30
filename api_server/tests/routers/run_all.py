import importlib
import os
import sys

def main():
    print("🔎 Discovering test modules...")
    print("=" * 50)

    results = {}
    all_passed = True

    # Directory where this script lives
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, base_dir)  # ensure import works

    # Look for files matching test_*.py
    for filename in os.listdir(base_dir):
        if not filename.startswith("test_") or not filename.endswith("_router.py"):
            continue

        module_name = filename[:-3]  # strip ".py"

        print(f"\n📦 Loading test module: {module_name}")

        try:
            module = importlib.import_module(module_name)
        except Exception as e:
            print(f"❌ Failed to import {module_name}: {e}")
            continue

        if hasattr(module, "run_all_tests"):
            print(f"▶️ Running {module_name}.run_all_tests()")
            try:
                passed = module.run_all_tests()
            except Exception as e:
                print(f"💥 Test crash in {module_name}: {e}")
                passed = False
            results[module_name] = passed
            if not passed:
                all_passed = False
        else:
            print(f"⚠️ {module_name} has no run_all_tests()")

    print("\n📊 GLOBAL TEST SUMMARY")
    print("=" * 50)
    for mod, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {mod}")

    if all_passed:
        print("\n🎉 ALL MODULES PASSED!")
        return 0
    else:
        print("\n💥 SOME MODULES FAILED!")
        return 1

if __name__ == "__main__":
    exit(main())
