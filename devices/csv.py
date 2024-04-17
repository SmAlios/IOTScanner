from os import path, makedirs

class CSV:

    # A CSV library already exist in Python but let's face it, it's a litle bit limited.
    # So I made another class to use CSV, beter build than the existing one (for this project).
    # The existing library can only add values in a CSV onece. I need to be able to write the header
    # and constantly adding data with a loop later.
    
    def __init__(self, csv_dir):
        self.CSV_dir = csv_dir

        # Create the specified directory if it don't exist
        try:
            if path.exists(self.CSV_dir) == False:
                makedirs(self.CSV_dir)
        except:
            #folder already exist
            pass

    # Write the header of the given file, header sections must be given
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

    # Write a row of data in the CSV file
    def write_csv_line(self, file, fields, data, deleted=None):
        with open(file, "a") as file:

            i = 1
            tmp = ""

            # The data are formated the look good in the CSV file
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