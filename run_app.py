import sys
import traceback

try:
    import main
except Exception as e:
    print("\nError occurred while running the application:")
    print(traceback.format_exc())
    input("\nPress Enter to exit...")
