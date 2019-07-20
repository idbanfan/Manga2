import os,sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class Manga(QWidget):

    def __init__(self):
        super(Manga, self).__init__()
        # Ui_Viewer().setupUi(self)

        self.tree = QTreeWidget(self)
        # 设置列数
        self.tree.setColumnCount(1)
        # 设置头的标题
        self.tree.setHeaderLabels(['tonjinshi'])
        item = QTreeWidgetItem(self.tree)
        #一行一列
        item.setText(0, 'like')

        # item2 = QTreeWidgetItem(self.tree)
        QTreeWidgetItem(self.tree).setText(0, 'favourite')

        Model
        sub_item = QTreeWidgetItem(item)
        sub_item.setText(0, 'artist')

        #确认点击信号
        self.tree.clicked.connect(self.onTreeClicked)

    def onTreeClicked(self,):
        item3 = self.tree.currentItem()
        print("key=%s ,value=%s" % (item3.text(0), item3.text(1)))


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