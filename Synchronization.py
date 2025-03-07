import os
import shutil
import logging
import argparse
import hashlib
import time


def calculate_md5(file_path, chunk_size=4096):
    '''Calculate the MD5 hash of a file using the built-in hashlib library'''

    md5 = hashlib.md5()

    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            md5.update(chunk)

    return md5.hexdigest()
    

def sync_file(source, replica):

    #If replica does not exist, make a copy
    if not os.path.exists(replica):
        shutil.copy2(source, replica)
        logging.info(f"Copied new file: {source} -> {replica}")
        return

    if calculate_md5(source) != calculate_md5(replica):
        shutil.copy2(source, replica)
        logging.info(f"Update file: {source} -> {replica}")
    
        

def sync_directories(source, replica):

    # Verify and ensure that replica file exists

    if not os.path.exists(replica):
        os.makedirs(replica)
        logging.info(f"Created directory: {replica}")

    #Sync files and subdirectories from source to replica

    for item in os.listdir(source):
        src_path = os.path.join(source, item)
        rep_path = os.path.join(replica, item)

        if os.path.isdir(src_path): #Recursively synchroniza subdirectories

            sync_directories(src_path, rep_path)

        else: #Handles files: copy if missing or update if different

            if not os.path.exists(rep_path): #If path to replica does not exist copy from source

                shutil.copy2(src_path, rep_path)
                logging.info(f"Copied new file: {src_path} -> {rep_path}")

            else: # If it exists Check for differences using MD5

                if calculate_md5(src_path) != calculate_md5(rep_path):
                    shutil.copy2(src_path, rep_path)
                    logging.info(f"Updated file: {src_path} -> {rep_path}")

    #Remove extra files and directories from replica

    for item in os.listdir(replica):
        rep_path = os.path.join(replica,item)
        src_path = os.path.join(source,item)

        if not os.path.exists(src_path):
            if os.path.isfile(rep_path):
                os.remove(rep_path)
                logging.info(f"Removed file: {rep_path}")

            elif os.path.isdir(rep_path):
                shutil.rmtree(rep_path)
                logging.info(f"Removed directory: {rep_path}")
        

def main():
    #Parsing command-line arguments
    parser = argparse.ArgumentParser(description="One-way Folder Synchronization Tool")
    parser.add_argument("source", help="Path to source folder")
    parser.add_argument("replica", help="Path to replica folder")
    parser.add_argument("interval", type = int, help="Synchronization interval in seconds")
    parser.add_argument("logfile", help="Path to log file")
    args = parser.parse_args()



    #Set up logging to both a file and the console

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(args.logfile), logging.StreamHandler()])


    logging.info("Starting folder synchronization")
    logging.info(f"Source Folder: {args.source}")
    logging.info(f"Replica Folder: {args.replica}")
    logging.info(f"Interval: {args.interval} seconds")
    
    #Run synchronization periodically
    while True:
        try:
            if os.path.isdir(args.source):
                sync_directories(args.source, args.replica)
            elif os.path.isfile(args.source):
                sync_file(args.source, args.replica)
            else:
                logging.error(f"Source path does not exist: {args.source}")

            logging.info("Synchronization completed")
            time.sleep(args.interval)

        except KeyboardInterrupt:
            logging.info("Synchronization interrupted by user. Exiting...")
            break

        except Exception as e:
            logging.error(f"Error during synchronization: {e}")
            time.sleep(args.interval)
if __name__ == '__main__':
     main()
