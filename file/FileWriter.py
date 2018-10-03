import os

class FileWriter():
    def __init__(self, directory, filename):
        self._directory = directory
        self._filename = filename

    def write_list(self, lines):
        self.make_dir()
        file_path = self._directory + "/" + self._filename
        f = open(file_path, "w+")
        for line in lines:
            f.write(line + "\n")
        f.close()
        return file_path

    def make_dir(self):
        if not os.path.exists(self._directory):
            os.makedirs(self._directory)