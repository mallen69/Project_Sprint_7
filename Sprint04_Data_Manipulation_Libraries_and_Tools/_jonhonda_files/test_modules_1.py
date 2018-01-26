import os
def test():
    print ('hello')

def remFile(filepath):
    try:
        os.remove(filepath)
        print ('file removed')
    except FileNotFoundError as err:
        print ("no need to remove file")####it's okay if file doesn't exist. ####
