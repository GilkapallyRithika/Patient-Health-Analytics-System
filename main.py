"""
main.py
Entry point for the Patient Health Analytics System.
Run with: python3 main.py
"""

import sys
import os

# Ensure sibling modules are importable regardless of working directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from user_interface_module import HealthAnalyticsApp


def main():
    app = HealthAnalyticsApp()
    app.mainloop()


if __name__ == "__main__":
    main()
