def write_to_file(urls):
    make_dir(directory)
    filename = directory + "/urls.txt"
    f = open(filename, "w+")
    for url in urls:
        f.write(url + "\n")
    print(" -> URLs are written to file " + filename)
    f.close()

    

def make_dir(dir):
    if not path.exists(dir):
        makedirs(dir)