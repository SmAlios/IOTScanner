from os import system, path, makedirs
from datetime import datetime
from time import sleep

# Compress the logs gathered while scanning
class Compress:
    def __init__(self, csv_to_compress):
        self.archives_dir = "archives"
        self.csv_to_compress = csv_to_compress

        # The of the archive is based on the date and time
        # The archive's name can't containe spaces or ":", so it's formated
        a,b = str(datetime.now()).split(" ")
        b1,b2,b3 = b.split(":")
        date = a+"_"+b1+"-"+b2+"-"+b3
        self.archive_name = f"scan_{date}.zip"

    # Launch the compression
    def launch(self):
        self.compress()

        # Freez the button on screen to get the time to compress
        sleep(3)

        self.delete_old_files()

        print("compression done and old files deleted")

    # Function'll check if archive directory exist, if it's not the case, it 'll be created
    def compress(self):
        try:
            if path.exists(self.archives_dir) == False:
                makedirs(self.archives_dir)
        except FileExistsError:
            #folder already exist
            pass
        
        # Use a Linux command to compress the archive
        system(f"zip {self.archives_dir}/{self.archive_name} {self.csv_to_compress}/*")

    def delete_old_files(self):
        # Use a Linux command to delete files in the specified directory
        system(f"rm {self.csv_to_compress}/*")