import json


class Data:
    def __init__(self, file_name):
        """Initializes and stores file name and the data on the file."""
        self.file_name = file_name
        # If the file exists it will be loaded, if not a new file is made.
        try:
            with open(self.file_name) as infile:
                self.data = json.load(infile)
        except FileNotFoundError:
            with open(self.file_name, 'w') as outfile:
                self.data = {}
                json.dump(self.data, outfile, indent=4)

    def load_master_dict(self, master_dict_name):
        """Loads specified master dictionary."""
        try:
            dictionary = self.data[str(master_dict_name)]
            return dictionary
        except KeyError:
            print(f'''Master '{master_dict_name}' dictionary does not exist in '{self.file_name}'!''')

    def append_file(self, dict_name, updated_data):
        """Adds data for a specified master dictionary."""
        try:
            self.data[dict_name].append(updated_data)
        # If the master dictionary doesn't exist a new one is made.
        except KeyError:
            self.data[dict_name] = []
            self.data[dict_name].append(updated_data)

    def update_file(self, dict_name, updated_data):
        try:
            self.data[dict_name] = updated_data
        # If the master dictionary doesn't exist a new one is made.
        except KeyError:
            self.data[dict_name] = []
            self.data[dict_name].append(updated_data)

    def save_to_file(self):
        """Saves data stored in self.data to the file it came from."""
        with open(self.file_name, 'w') as outfile:
            json.dump(self.data, outfile, indent=4)

""" Data is stored in the format:
    Data = { Master Dictionaries...
        [ List in a Master Dictionary...
            { Sub Dictionaries in List...
                }]}"""
