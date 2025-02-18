import sys
import traceback

try:
    from gui import main
except Exception as e:
    print("\nError occurred while running the application:")
    print(traceback.format_exc())
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
