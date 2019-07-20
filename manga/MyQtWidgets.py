from __future__ import print_function
import os,sys,shutil
import re
from requests.packages import urllib3
import pymongo

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QWidget

from manga.download_gui import Ui_ExDownload

from manga.image_gui import Ui_MyImage
from manga.resycle_gui import Ui_MyResycle
from manga.resycle_item_gui import Ui_MyResycleItem
from manga.input_gui import Ui_MyInput
from manga.scroll_area_gui import Ui_ScrollArea

from win32com.shell import shell,shellcon
from manga.LittleWidgets import MyTagQuickLabel, Downloader
urllib3.disable_warnings()

class MyImage(QWidget,Ui_MyImage):
    def __init__(self,parent=None):
        super(MyImage, self).__init__(parent)
        self.setupUi(self)
        # dataBase
        myclient = pymongo.MongoClient('mongodb://localhost:27017/')
        data_base = myclient["local"]
        self.tag_table = data_base['tag_table']
        self.item_table = data_base['item_table']

        # avg
        self.item_type = 'manga_product'
        self.images_path = None
        self.image_files = None
        self.image_file_index = 0

        # connect
        self.pushButton_addTag.clicked.connect(self.create_input)

        self.labelImage.clicked_left.connect(self.next_image)
        self.labelImage.clicked_right.connect(self.previous_image)

        self.pushButton_delete.clicked.connect(self.delete)
        self.pushButtonOpen.clicked.connect(self.open)

        # init

    def load_image_path(self,images_path):
        self.images_path = images_path
        self.image_files = os.listdir(images_path)
        self.label_page.setText(str(len(self.image_files)))
        self.__set_image(self.image_file_index)
        self.__set_name()
        self.load_tags()


    def create_input(self):
        self.input = MyInput('manga_product',self.images_path)
        self.input.pushButton_ok.clicked.connect(self.load_tags)
        self.input.show()

    def load_tags(self):
        path = self.images_path
        result = self.item_table.find_one({'path':path})
        if result:
            tags = result['tags']
            if tags:
                self.label_tag.setText(';'.join(tags))
        else:
            self.item_table.insert_one({'path':path,'tags':[],'item_type':self.item_type})


    def __set_image(self,image_file_index):
        first_image = self.image_files[image_file_index]


        imagePath = os.path.join(self.images_path, first_image)
        self.labelImage.setImage(imagePath)

    def __set_name(self):
        name = self.images_path.split('\\')[-1]
        maxlen = 50
        if len(name)>maxlen:
            half = int(maxlen/2)
            name = name[:half]+'..'+name[-half:]
        self.label_name.setText(name)

    def next_image(self):
        if self.image_file_index < len(self.image_files)-1:
            self.image_file_index += 1
            self.__set_image(self.image_file_index)

    def previous_image(self):
        if self.image_file_index > 0 :
            self.image_file_index -= 1
            self.__set_image(self.image_file_index)

    def delete(self):
        delete_bin(self.images_path)
        self.close()

    def open(self):
        program  = r'E:\soft安装软件\Honeyview\Honeyview.exe'
        path = os.path.join(self.images_path,self.image_files[self.image_file_index])
        cmd = '{} {}'.format(program, path.replace('\\','/'))
        os.startfile(path)
        #os.system(cmd)

    def get_path(self):
        return self.images_path


class MyRecycle(QWidget):
    def __init__(self,parent=None):
        super(MyRecycle, self).__init__(parent)
        Ui_MyResycle().setupUi(self)


class MyRecycleItem(QWidget):
    def __init__(self,parent=None):
        super(MyRecycleItem, self).__init__(parent)
        Ui_MyResycleItem().setupUi(self)


class MyInput(QWidget,Ui_MyInput):
    msg = pyqtSignal(str)
    tag_text = pyqtSignal(str)
    write_tags = pyqtSignal()
    def __init__(self,tag_type,path,parent=None):
        super(MyInput, self).__init__(parent)
        self.setupUi(self)

        # 数据库
        self.my_client = pymongo.MongoClient('mongodb://localhost:27017/')
        self.tag_data_base = self.my_client['local']
        self.tag_table = self.tag_data_base['tag_table']
        self.item_table = self.tag_data_base['item_table']

        # 信号连接
        #self.pushButton_ok.clicked.connect(self.hide)
        self.pushButton_ok.clicked.connect(self.write_tags)
        self.pushButton_ok.clicked.connect(self.close)

        # 属性
        self.path = path
        self.item =None
        self.tags =None   # type = None/list/dict
        self.tag_type = tag_type
        self.prepare_write_tags = list()
        self.quick_tag_labels = list()

        # 初始化
        self.load_tags()
        self.show_tags()

    def load_tags(self):
        if self.tag_type in ['manga_product']:# has sub_tag
            self.tags = dict()
            for each in self.tag_table.find({'tag_type':self.tag_type}):
                sub_type = each['sub_type']
                tag = each['tag_name']
                if sub_type not in self.tags:
                    self.tags[sub_type] = list()
                self.tags[sub_type].append(tag)
        elif self.tag_type in ['animation_company','animation_product','animation_video','manga_artist','manga_image','image']:
            self.tags = list()
            for each in self.tag_table.find({'tag_type':self.tag_type}):
                tag = each['tag_name']
                self.tags.append(tag)
        else:
            # 输入 tag_type 没有
            raise TypeError

    def show_tags(self):
        if isinstance(self.tags,list):
            swap = 5
            for count, tag in enumerate(self.tags):
                row = count / swap
                col = count % swap
                quick_tag_label = MyTagQuickLabel()
                quick_tag_label.setFrameShape(QFrame.Box)
                quick_tag_label.add_tag.connect(self.add_prepare_tags)
                quick_tag_label.remove_tag.connect(self.remove_prepare_tags)
                quick_tag_label.setMinimumSize(QSize(70, 30))
                quick_tag_label.setText(tag)
                self.gridLayout.addWidget(quick_tag_label, row, col)
                self.quick_tag_labels.append(quick_tag_label)
        else:
            row = 0
            col = 0
            for sub_type in self.tags.keys():
                sub_type_label = QLabel()
                sub_type_label.setText(sub_type)
                sub_type_label.setFrameShape(QFrame.Box)
                sub_type_label.setMinimumSize(QSize(70, 30))
                self.gridLayout.addWidget(sub_type_label, row, col)
                col += 1
                for tag in self.tags[sub_type]:
                    quick_tag_label = MyTagQuickLabel()
                    quick_tag_label.setFrameShape(QFrame.Box)
                    quick_tag_label.add_tag.connect(self.add_prepare_tags)
                    quick_tag_label.remove_tag.connect(self.remove_prepare_tags)
                    quick_tag_label.setMinimumSize(QSize(70, 30))
                    quick_tag_label.setText(tag)
                    self.gridLayout.addWidget(quick_tag_label, row, col)
                    self.quick_tag_labels.append(quick_tag_label)
                    col += 1
                col = 0
                row += 1

    def write_tags(self):
        if self.prepare_write_tags :
            #有记录->更新
            if self.item_table.find_one({'path':self.path}):
                self.item_table.update_one({'path':self.path}, { "$set": {'tags':self.prepare_write_tags}})
            #无记录->插入
            else:
                self.item_table.insert_one({'path':self.path,'item_type':self.tag_type,'tags':self.prepare_write_tags})

    def add_prepare_tags(self,tag:str):
        self.prepare_write_tags.append(tag)

    def remove_prepare_tags(self, tag:str):
        self.prepare_write_tags.remove(tag)

    def clear_prepare_tags(self):
        self.prepare_write_tags.clear()
        for label in self.quick_tag_labels:
            label.setFrameShape(QFrame.NoFrame)


class ExDownload(QWidget,Ui_ExDownload):

    download_signal = pyqtSignal(str, str)
    print_signal = pyqtSignal(str)

    def __init__(self,parent=None):
        super(ExDownload, self).__init__(parent)
        self.setupUi(self)

        self.print_signal.connect(self.textBrowser.append)

        self.pushButtonDownload.clicked.connect(self.download)
        self.pushButtonStop.clicked.connect(self.stop_thread)
        self.pushButtonClear_2.clicked.connect(self.textBrowser.clear)

        self.init_download()

    def download(self):
        url = self.__get_url()
        path = self.__get_path()
        if url and path:
            self.download_signal.emit(url,path)
            self.print_signal.emit('## ST : {}'.format(url))
        else:
            self.print_signal.emit('地址或路径错误')

    def init_download(self):
        self.thread = QThread()
        self.Downloader = Downloader()
        self.Downloader.moveToThread(self.thread)
        self.Downloader.print_signal.connect(self.textBrowser.append)
        self.download_signal.connect(self.Downloader.download)
        self.thread.start()

    def stop_thread(self):
        self.thread.exit()

    def __get_path(self):
        path =  self.FilePathEdit.text()
        return path

    def __get_url(self):
        url =  self.URLEdit.text()
        if re.search('https://exhentai.org/g/.*?/.*?/', url):
            return url
        else:
            return None

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key() == Qt.Key_Q:
            self.textBrowser.clear()
        elif a0.key() == Qt.Key_E:
            self._refresh()
        elif a0.key() == Qt.Key_Escape:
            self.close()


class ImageScrollArea(QScrollArea, Ui_ScrollArea):
    def __init__(self,parent=None):
        super(ImageScrollArea, self).__init__(parent)
        self.setupUi(self)
        self.run_image_widget_paths = list()
        self.manga_paths = None
        self.running_image_widegts_num = 0
        self.row = 0
        self.running_widgets = list()
        #

    def load_image_widgets(self,artist_path:str,swap=2):
        self.manga_paths = [os.path.join(artist_path,rel_manga_path) for rel_manga_path in os.listdir(artist_path)]
        for count,manga_path in enumerate(self.manga_paths[:4]):
            row = int(count/swap)
            col = count % swap
            self.create_image_widget(manga_path, row, col)

        self.row += 2

    def reload_image_widgets(self, swap=2):
        for count, manga_path in enumerate(self.manga_paths[self.row * swap:self.row * swap + swap]):
            col = count % swap
            self.create_image_widget(manga_path, self.row, col)
        self.row += 1

    def create_image_widget(self, manga_path:str, row, col):

        image_widget = MyImage(self.scrollAreaWidgetContents)
        image_widget.load_image_path(manga_path)
        self.running_widgets.append(image_widget)

        self.gridLayout.addWidget(image_widget,row,col)
        self.run_image_widget_paths.append(manga_path)

    def load_check(self,manga_path,row):
        if row > 0:
            if  self.verticalScrollBar().value() == self.verticalScrollBar().maximum() and \
                    manga_path not in self.run_image_widget_paths:

                return True
            else:
                return False
        else:
            return True

    def clear_image_widgets(self):
        for each in self.running_widgets:
            each.close()

    def wheelEvent(self, a0):
        bar = self.verticalScrollBar()
        bar.setValue(bar.value() - a0.angleDelta().y())
        if self.verticalScrollBar().value() == self.verticalScrollBar().maximum():
            self.reload_image_widgets()


def delete_bin(filename):
    res= shell.SHFileOperation((
        0,
        shellcon.FO_DELETE,
        filename,
        None,
        shellcon.FOF_SILENT | shellcon.FOF_ALLOWUNDO | shellcon.FOF_NOCONFIRMATION,
        None,
        None
    ))
    if not res[1]:
        os.system('del '+filename)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    test_info = 'ImageScrollArea'

    if test_info == 'MyImage':
        path = r'E:\pythonPorject\Manga\data\tonjinshi_like\MANA\表情吃鸡'
        down_widget = MyImage(path)
        down_widget.show()

    if test_info == 'ExDownload':
        down_widget = ExDownload()
        down_widget.show()

    if test_info == 'MyInput':
        down_widget = MyInput('manga_product')
        down_widget.show()

    if test_info == 'ImageScrollArea':
        down_widget = ImageScrollArea()
        down_widget.load_image_widgets(r'E:\pythonPorject\Manga\data\tonjinshi_like\MANA')
        down_widget.show()

    sys.exit(app.exec_())