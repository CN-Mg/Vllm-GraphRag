#!/usr/bin/env python3
"""
Final comprehensive test to verify all imports work correctly
"""

import sys
import traceback

def test_import(module_name, import_statement):
    """Test a specific import"""
    try:
        exec(import_statement)
        print(f"✓ {module_name}: {import_statement}")
        return True
    except ImportError as e:
        print(f"❌ {module_name}: {import_statement}")
        print(f"   Error: {e}")
        return False
    except Exception as e:
        print(f"❌ {module_name}: {import_statement}")
        print(f"   Unexpected error: {e}")
        return False

def main():
    print("Starting final import test...\n")

    # Test all critical imports
    tests = [
        ("Main module", "from src.main import *"),
        ("Shared functions", "from src.shared.common_fn import *"),
        ("LLM module", "from src.llm import get_llm"),
        ("Constants", "from src.shared.constants import MODEL_VERSIONS"),
        ("Image analysis", "from src.image_analysis import analyze_image_with_vlm"),
        ("Graph documents", "from src.generate_graphDocuments_from_llm import generate_graphDocuments"),
        ("Create chunks", "from src.create_chunks import CreateChunksofDocument"),
        ("Graph DB access", "from src.graphDB_dataAccess import graphDBdataAccess"),
        ("Source node", "from src.entities.source_node import sourceNode"),
        ("Document sources", "from src.document_sources.local_file import get_documents_from_file_by_path"),
        ("Web pages", "from src.document_sources.web_pages import *"),
        ("Graph transformers", "from src.graph_transformers.llm import LLMGraphTransformer"),
        ("QA integration", "from src.QA_integration_new import *"),
    ]

    passed = 0
    failed = 0

    for module_name, import_statement in tests:
        if test_import(module_name, import_statement):
            passed += 1
        else:
            failed += 1
        print()

    print(f"Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("\n🎉 All imports successful! The backend should start without errors.")
    else:
        print(f"\n⚠️  {failed} import(s) failed. Please check the errors above.")

    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)