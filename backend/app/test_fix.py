import sys
import os

# Add current directory to sys.path so we can import services
sys.path.append(os.getcwd())

try:
    from services.intent_service import intent_service

    print("Successfully imported intent_service")
    print(f"System Instruction defined: {len(intent_service.system_instruction) > 0}")
    print("Verification passed!")
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)
except AttributeError as e:
    print(f"AttributeError: {e}")
    sys.exit(1)
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)
