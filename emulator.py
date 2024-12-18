import zipfile
import argparse
import configparser
import os

class Virtual_System:
    def __init__(self, zip_path):
        self.zip_path = zip_path
        self.current_dir = '/'
        self.file_structure = {}
        self.load_zip()

    def load_zip(self):
        with zipfile.ZipFile(self.zip_path, 'r') as z:
            for obj_path in z.namelist():
                if obj_path == 'access_rights.txt':
                    continue
                parts = obj_path.strip('/').split('/')
                current_level = self.file_structure
                for part in parts:
                    is_file = part == parts[-1] and not obj_path.endswith('/')
                    if is_file:
                        current_level[part] = {
                            "type": "file"
                        }
                    else:
                        if part not in current_level:
                            current_level[part] = {
                                "type": "folder",
                                "list_f": {}
                            }
                        current_level = current_level[part]["list_f"]

    def cd(self, path):
        if path == '~':
            self.current_dir = '/'
            return
        parsed_path = self.path_parser(path)
        if self.dictionary(parsed_path) is None:
            print(f"cd: {path}: нет такого каталога(")
        else:
            self.current_dir = parsed_path

    def path_parser(self, path):
        if path.startswith("/"):
            abs_path = path
        else:
            abs_path = self.current_dir + path
        parts = abs_path.split('/')
        final_parts = []
        for part in parts:
            if part == '' or part == '.':
                continue
            elif part == "..":
                if final_parts:
                    final_parts.pop()
            else:
                final_parts.append(part)
        final_path = '/' + '/'.join(final_parts) + '/'
        final_path = final_path.replace('//', '/')
        if final_path == '':
            final_path = '/'
        return final_path

    def dictionary(self, path):
        if path == "/":
            return self.file_structure
        parts = path.strip('/').split('/')
        current_level = self.file_structure
        for part in parts:
            if part in current_level:
                if current_level[part]["type"] == "folder":
                    current_level = current_level[part]["list_f"]
                else:
                    return None
            else:
                return None
        return current_level

    def ls(self, path="."):
        parsed_path = self.path_parser(path)
        directory_dict = self.dictionary(parsed_path)
        return path, directory_dict

class Emulator:
    def __init__(self, username, hostname, vfs):
        self.username = username
        self.hostname = hostname
        self.vfs = vfs

    def whoami(self):
        return self.username

    def rev(self, file_path):

        full_path = os.path.join(self.vfs.current_dir, file_path).replace("\\", "/")

        try:
            with zipfile.ZipFile(self.vfs.zip_path, 'r') as z:

                if full_path[1:] in z.namelist():
                    with z.open(full_path[1:]) as file:
                        for line in file:
                            return line.decode("utf-8").strip()[::-1]
                else:
                    print(f"rev: {file_path}: No such file in the zip archive. Reversing the string.")
                    return file_path[::-1]

        except Exception as e:
            print(f"Error reading file: {e}")

    def run(self):
        while True:
            print(f"{self.username}@{self.hostname}:{self.vfs.current_dir}$ ", end="")
            line = input().strip()
            if not line:
                continue
            parts = line.split()
            command = parts[0]
            args = parts[1:]

            if command == "exit":
                break
            elif command == "cd":
                if len(args) == 1:
                    self.vfs.cd(args[0])
            elif command == "ls":
                if len(args) == 0:
                    path, directory_dict = self.vfs.ls()
                else:
                    path, directory_dict = self.vfs.ls(args[0])
                if directory_dict is None:
                    print(f"ls: {path}: такого каталога нет(")
                else:
                    print("\n".join(sorted(directory_dict.keys())))

            elif command == "whoami":
                print(self.whoami())

            elif line.startswith("rev "):
                print(self.rev(line[4:]))

            else:
                print(f"Такую команду нельзя использовать: {line} ")
        print("Удачи!!!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Shell Emulator")
    parser.add_argument("config", help="Path to the configuration file")
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.config)
    username = config['DEFAULT']['username']
    hostname = config['DEFAULT']['hostname']
    filesystem_path = config['DEFAULT']['filesystem_path']

    vfs = Virtual_System(filesystem_path)
    shell = Emulator(username, hostname, vfs)
    shell.run()
