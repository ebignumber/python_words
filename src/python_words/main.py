"""Main entry point for Python Words application."""

import os
import sys
import subprocess

# Add the package root to the path so we can import the modules
PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PACKAGE_ROOT)


def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def show_menu():
    """Display the main menu and handle user selection."""
    while True:
        clear_screen()
        print("Welcome to Python Words!\n")
        print("What would you like to do?\n")
        print("1. Create Puzzles")
        print("2. Play Puzzles")
        print("3. Exit\n")
        
        try:
            selection = input("Choose an option: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye")
            break
            
        print("\n")
        
        if selection == '1':
            # Run puzzle creator
            run_puzzle_creator()
        elif selection == '2':
            # Run word finder
            run_word_finder()
        elif selection == '3':
            print("bye")
            break
        else:
            print("Invalid response")
            input("Press Enter to continue...")


def run_puzzle_creator():
    """Run the puzzle creator module."""
    # Change to the package root directory
    original_dir = os.getcwd()
    try:
        # Change to the package root so relative paths work
        os.chdir(PACKAGE_ROOT)
        from python_words.puzzle_creator import main as puzzle_creator_main
        puzzle_creator_main()
    except ImportError:
        # Fallback: run the original script
        python_path = os.path.join(PACKAGE_ROOT, "python", "puzzle_creator.py")
        if os.path.exists(python_path):
            subprocess.run([sys.executable, python_path], check=True)
        else:
            print("Error: Could not find puzzle_creator module")
            input("Press Enter to continue...")
    except Exception as e:
        print(f"Error running puzzle creator: {e}")
        input("Press Enter to continue...")
    finally:
        os.chdir(original_dir)


def run_word_finder():
    """Run the word finder module."""
    original_dir = os.getcwd()
    try:
        os.chdir(PACKAGE_ROOT)
        from python_words.wordfinder import main as wordfinder_main
        wordfinder_main()
    except ImportError:
        # Fallback: run the original script
        python_path = os.path.join(PACKAGE_ROOT, "python", "wordfinder.py")
        if os.path.exists(python_path):
            subprocess.run([sys.executable, python_path], check=True)
        else:
            print("Error: Could not find wordfinder module")
            input("Press Enter to continue...")
    except Exception as e:
        print(f"Error running word finder: {e}")
        input("Press Enter to continue...")
    finally:
        os.chdir(original_dir)


def main():
    """Main entry point function."""
    show_menu()


if __name__ == "__main__":
    main()
