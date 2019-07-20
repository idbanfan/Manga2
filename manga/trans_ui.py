import os

for each in os.listdir(r'E:\pythonPorject\Manga\manga'):
    if each[-3:] == '.ui':
        print(each)
        file_py = each.replace('.ui','.py')
        cmd= 'D:\Anaconda3\python.exe -m PyQt5.uic.pyuic {} -o {}'.format(each,file_py)
        os.system(cmd)