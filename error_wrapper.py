
import sys
import traceback

try:
    import main
except Exception as e:
    print("Error occurred while running the application:")
    print(traceback.format_exc())
    input("Press Enter to exit...")
    sys.exit(1)
