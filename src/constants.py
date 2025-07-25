class FileLocations:
    # All of the file locations that will be backed up
    ORIGINAL_FILE_LOCATIONS = ["C:/Users/world/Downloads"]

    # All of the locations where backups will be stored
    BACKUP_LOCATIONS = ["C:/Backups"]

    # Name of the zip file created for backup
    BACKUP_FILE_NAME = "backup"

    # Default timeout for subprocess calls
    DEFAULT_TIMEOUT = 10  # seconds

    # Number of CPU threads to use for ZIP compression (0 = auto-detect)
    ZIP_THREADS = 0  # 0 means use min(4, cpu_count())

    # ZIP compression level (1-9, higher = better compression but slower)
    ZIP_COMPRESSION_LEVEL = 6  # Good balance of speed and compression

    # Hashing optimization settings
    HASH_BUFFER_SIZE_MB = 8  # Buffer size in MB for file hashing (increased from 1MB)
    HASH_THREADS = 0  # Number of threads for parallel hashing (0 = auto-detect)
    USE_MEMORY_MAPPING = True  # Use memory mapping for large files (>50MB)
    MEMORY_MAP_THRESHOLD_MB = 50  # Files larger than this will use memory mapping
