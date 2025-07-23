import sys
from backup_workflow import execute_backup_workflow


def main():
    """Main execution function for the backup system."""
    success = execute_backup_workflow()
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
