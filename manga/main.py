import os,sys,time

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from manga.main_gui import Ui_Manga
from manga.MyQtWidgets import MyImage


class Manga(QWidget,Ui_Manga):

    def __init__(self, parent=None, data_path=r'G:\ACG\PICTURE'):
        super(Manga, self).__init__()
        self.setupUi(self)

        self.runImageWidgets = list()

        self.artistTree.setHeaderLabels(['artist','num'])

        self.data_path = data_path
        self.init_tree(self.data_path)

        self.artistTree.clicked.connect(self.tree_clicked)

        self.artistTree.currentPath = None

    def initArtist(self, artist_path:str):
        imageWidgets = self.create_imageWidgets(artist_path)
        self.append_images(imageWidgets)

    def changeArtist(self, artist_path:str):
        self.clear_runImageWidgets()
        self.initArtist(artist_path)

    def create_imageWidgets(self, artist_path):
        for rel_comic_path in os.listdir(artist_path):
            abs_comic_path = os.path.join(artist_path,rel_comic_path)
            if os.path.isdir(abs_comic_path):
                t = MyImage()
                t.load_image_path(abs_comic_path)
                yield t

    def append_image(self, imageWidget, row, col):
        self.runImageWidgets.append(imageWidget)
        self.gridLayout.addWidget(imageWidget, row, col)

    def append_images(self, imageWidgets, swap=2):
        for count,imageWidget in enumerate(imageWidgets):
            row = count / swap
            col = count % swap
            self.append_image(imageWidget,row,col)

    def clear_runImageWidgets(self):
        for imageWidget in self.runImageWidgets:
            imageWidget.close()

    def append_item(self,text):
        item = QTreeWidgetItem(self.artistTree)
        item.setText(0, text)

    def append_sub_item(self, item_text, sub_item_text,num):
        item = self.artistTree.findItems(item_text, Qt.MatchExactly)[0]
        sub_item = QTreeWidgetItem(item)
        sub_item.setText(0, sub_item_text)
        sub_item.setText(1, num)

    def init_tree(self,data_path,keyWord='tonjinshi'):
        for artists_path in os.listdir(data_path):
            if keyWord in artists_path:
                self.append_item(artists_path)
                for artist_path in os.listdir(os.path.join(data_path,artists_path)):
                    num = str(len(os.listdir(os.path.join(data_path,artists_path,artist_path))))
                    self.append_sub_item(artists_path,artist_path,num)

    def tree_clicked(self):
        sub_item = self.artistTree.currentItem()
        if sub_item.parent() != None:
            self.artistTree.currentPath = os.path.join(self.data_path,sub_item.parent().text(0),sub_item.text(0))
            self.changeArtist(self.artistTree.currentPath)
        else:
            self.artistTree.currentPath = None

    def delete(self):
        pass

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key() == Qt.Key_Q:
            pass

        elif a0.key() == Qt.Key_E:
            pass

def main_window():
    # 开启循环
    app = QApplication(sys.argv)
    # 主窗口
    down_widget = Manga()
    down_widget.show()

    # 退出
    sys.exit(app.exec_())

if __name__ == '__main__':
    main_window()