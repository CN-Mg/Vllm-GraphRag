#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

try:
    print("Testing imports...")

    # Test main imports
    from src.main import *
    print("✓ Main imports successful")

    # Test shared functions
    from src.shared.common_fn import *
    print("✓ Shared functions imports successful")

    # Test LLM imports
    from src.llm import get_llm
    print("✓ LLM imports successful")

    # Test constants
    from src.shared.constants import MODEL_VERSIONS
    print(f"✓ Constants loaded: {len(MODEL_VERSIONS)} models")

    # Test image analysis
    from src.image_analysis import analyze_image_with_vlm
    print("✓ Image analysis imports successful")

    print("\nAll imports successful! The backend should start without errors.")

except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()