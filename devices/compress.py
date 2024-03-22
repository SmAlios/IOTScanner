from os import system, path, makedirs
from datetime import datetime
from time import sleep
#handle an error of os.pth.makedir
import sys

class Compress:
    def __init__(self, csv_to_compress):
        self.archives_dir = "archives"
        self.csv_to_compress = csv_to_compress

        a,b = str(datetime.now()).split(" ")
        b1,b2,b3 = b.split(":")
        date = a+"_"+b1+"-"+b2+"-"+b3
        self.archive_name = f"scan_{date}.zip"

    def launch(self):
        self.compress()

        #get the time to compress
        sleep(3)

        self.delete_old_files()

        print("compression done and old files deleted")

    def compress(self):
        try:
            if path.exists(self.archives_dir) == False:
                makedirs(self.archives_dir)
        except FileExistsError:
            #folder already exist
            pass
        
        system(f"zip {self.archives_dir}/{self.archive_name} {self.csv_to_compress}/*")

    def delete_old_files(self):
        system(f"rm {self.csv_to_compress}/*")