from os import path, makedirs

class CSV:

    #another class to use CSV beter build than the existing library (for this project)
    #the existing library can only add values in a CSV ons (need to add a header at each write in file)
    
    def __init__(self, csv_dir):
        self.CSV_dir = csv_dir

        try:
            if path.exists(self.CSV_dir) == False:
                makedirs(self.CSV_dir)
        except FileExistsError:
            #folder already exist
            pass

    def write_csv_header(self, file, fields):
        with open(file, "a") as file:
            
            i = 1
            tmp = ""
            for element in fields:
                tmp += element

                if i < len(fields):
                    tmp += ";"
                i += 1

            file.write(f"{tmp}\n")


    def write_csv_line(self, file, fields, data, deleted=None):
        with open(file, "a") as file:

            i = 1
            tmp = ""

            #print(data)

            for element in str(data).split("(")[-1].split(")")[0].split(", "):

                if deleted == True and i == 1:
                        tmp += "[Deleted device] "

                elif element.split(":")[0] == "address":
                        tmp += element.split("address: ")[1]

                elif element.split(":")[0] == "BSSID":
                        tmp += element.split("BSSID:")[1]

                else:
                    tmp += element.split(":")[1]

                if i < len(fields):
                    tmp += ";"
                i += 1

            file.write(f"{tmp}\n")