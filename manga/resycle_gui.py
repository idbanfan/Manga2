# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'resycle_gui.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MyResycle(object):
    def setupUi(self, MyResycle):
        MyResycle.setObjectName("MyResycle")
        MyResycle.resize(362, 451)
        self.verticalLayout = QtWidgets.QVBoxLayout(MyResycle)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.pushButton = QtWidgets.QPushButton(MyResycle)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)
        self.scrollArea = QtWidgets.QScrollArea(MyResycle)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 360, 426))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)

        self.retranslateUi(MyResycle)
        QtCore.QMetaObject.connectSlotsByName(MyResycle)

    def retranslateUi(self, MyResycle):
        _translate = QtCore.QCoreApplication.translate
        MyResycle.setWindowTitle(_translate("MyResycle", "Form"))
        self.pushButton.setText(_translate("MyResycle", "清空"))

