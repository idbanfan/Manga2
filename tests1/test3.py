import os

path = r'G:\ACG\PICTURE'

for dirpath,dirnames,filenames in os.walk(path):
    for filename in filenames:
        if 'temp' in filename:
            s = 11 - len(filename)
            new_name = filename.replace('temp','0'*s)
            old_path = os.path.join(dirpath,filename)
            new_path = os.path.join(dirpath,new_name)
            os.rename(old_path,new_path)
            print(old_path)