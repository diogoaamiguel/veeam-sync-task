import os
import shutil
import logging
import argparse
import hashlib
import time

def calculate_md5(file_path, chunk_size=4096):
    '''Calculate the MD5 hash of a file'''
    md5 = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                md5.update(chunk)
        return md5.hexdigest()
    except Exception as e:
        logging.error(f"Error computing MD5 for {file_path}: {e}")
        return None

def sync_file(source, replica):
    if not os.path.exists(source):
        logging.error(f"Source file does not exist: {source}")
        return
    
    # If replica does not exist, make a copy
    if not os.path.exists(replica):
        if os.path.islink(source):
            os.symlink(os.readlink(source), replica)
            logging.info(f"Created symlink: {source} -> {replica}")
        else:
            shutil.copy2(source, replica)
            logging.info(f"Copied new file: {source} -> {replica}")
        return
    
    # Calculate MD5 hashes
    source_md5 = calculate_md5(source)
    replica_md5 = calculate_md5(replica)
    
    if source_md5 is None or replica_md5 is None:
        logging.error(f"Skipping {source} due to MD5 calculation error")
        return
    
    if source_md5 != replica_md5:
        shutil.copy2(source, replica)
        logging.info(f"Updated file: {source} -> {replica}")

def sync_directories(source, replica):
    """Recursively synchronize the source directory with the replica."""
    if not os.path.exists(replica):
        try:
            os.makedirs(replica)
            logging.info(f"Created directory: {replica}")
        except Exception as e:
            logging.error(f"Error creating directory {replica}: {e}")
            return
    
    # Get directory listing safely
    try:
        items = os.listdir(source)
    except Exception as e:
        logging.error(f"Could not list directory {source}: {e}")
        return
    
    # Sync files and subdirectories
    for item in items:
        if item.startswith('.'):  # Skip hidden files
            continue
        
        src_path = os.path.join(source, item)
        rep_path = os.path.join(replica, item)
        
        if os.path.isdir(src_path):
            sync_directories(src_path, rep_path)
        else:
            sync_file(src_path, rep_path)
    
    # Remove extra files and directories from the replica
    try:
        for item in os.listdir(replica):
            rep_path = os.path.join(replica, item)
            src_path = os.path.join(source, item)
            
            if not os.path.exists(src_path):
                try:
                    if os.path.isfile(rep_path) or os.path.islink(rep_path):
                        os.remove(rep_path)
                        logging.info(f"Removed file: {rep_path}")
                    elif os.path.isdir(rep_path):
                        shutil.rmtree(rep_path)
                        logging.info(f"Removed directory: {rep_path}")
                except Exception as e:
                    logging.error(f"Error removing {rep_path}: {e}")
    except Exception as e:
        logging.error(f"Error synchronizing directory {source}: {e}")

def main():
    # Parsing command-line arguments
    parser = argparse.ArgumentParser(description="One-way Folder Synchronization Tool")
    parser.add_argument("source", help="Path to source folder")
    parser.add_argument("replica", help="Path to replica folder")
    parser.add_argument("interval", type=int, help="Synchronization interval in seconds")
    parser.add_argument("logfile", help="Path to log file")
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(args.logfile), logging.StreamHandler()]
    )
    
    logging.info("Starting folder synchronization")
    logging.info(f"Source Folder: {args.source}")
    logging.info(f"Replica Folder: {args.replica}")
    logging.info(f"Interval: {args.interval} seconds")
    
    backoff_interval = args.interval
    max_backoff = 300  # 5 minutes
    
    # Run synchronization periodically
    while True:
        try:
            if os.path.isdir(args.source):
                sync_directories(args.source, args.replica)
            elif os.path.isfile(args.source):
                sync_file(args.source, args.replica)
            else:
                logging.error(f"Source path does not exist: {args.source}")
                break
                
            logging.info("Synchronization completed")
            time.sleep(args.interval)
            backoff_interval = args.interval  # Reset backoff interval after successful sync
        
        except KeyboardInterrupt:
            logging.info("Synchronization interrupted by user. Exiting...")
            break
        
        except Exception as e:
            logging.error(f"Error during synchronization: {e}")
            time.sleep(backoff_interval)
            backoff_interval = min(backoff_interval * 2, max_backoff)  # Corrected backoff logic

if __name__ == '__main__':
    main()
