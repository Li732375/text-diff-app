import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QTabWidget, QHBoxLayout, QPlainTextEdit, QScrollArea, QSizePolicy
from PyQt5.QtGui import QTextCursor, QColor, QTextCharFormat, QFont, QTextOption
from PyQt5.QtCore import Qt
from difflib import Differ

class TextDiffApp(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle('Text Diff Checker')
        self.resize(800, 600)

        mainlayout = QVBoxLayout(self) # 主佈局
        self.tabWidget = QTabWidget() # 分頁組
        self.initUI_Tab1()
        self.initUI_Tab2()
        self.tabWidget.setTabEnabled(1, False)  # 預設隱藏 Diff Tab

        mainlayout.addWidget(self.tabWidget)
        self.setLayout(mainlayout)

    def initUI_Tab1(self):
        # Input Tab
        self.inputTab = QWidget()

        inputTabLayout = QVBoxLayout(self.inputTab)

        self.textEdit1 = QTextEdit()
        self.textEdit1.setPlaceholderText("Enter first text here...")
        self.textEdit1.setStyleSheet("font-size: 16px;")

        self.textEdit2 = QTextEdit()
        self.textEdit2.setPlaceholderText("Enter second text here...")
        self.textEdit2.setStyleSheet("font-size: 16px;")

        self.compareButton = QPushButton('Compare')
        self.compareButton.clicked.connect(self.compareTexts)

        inputTabLayout.addWidget(self.textEdit1)
        inputTabLayout.addWidget(self.textEdit2)
        inputTabLayout.addWidget(self.compareButton)

        self.tabWidget.addTab(self.inputTab, "Input")
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.inputTab), "輸入要比較的文字")

    def initUI_Tab2(self):
        # Diff Tab
        self.leftTextEdit = QPlainTextEdit()
        self.leftTextEdit.setReadOnly(True)
        self.leftTextEdit.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.leftTextEdit.setFont(QFont("Courier New", 10))
        self.leftTextEdit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.leftTextEdit.verticalScrollBar().valueChanged.connect(self.syncScroll)

        self.rightTextEdit = QPlainTextEdit()
        self.rightTextEdit.setReadOnly(True)
        self.rightTextEdit.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.rightTextEdit.setFont(QFont("Courier New", 10))
        self.rightTextEdit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.rightTextEdit.verticalScrollBar().valueChanged.connect(self.syncScroll)

        # 建立水平佈局
        self.diffHLayout = QHBoxLayout()
        self.diffHLayout.addWidget(self.leftTextEdit)
        self.diffHLayout.addWidget(self.rightTextEdit)

        # 控制水平佈局伸展方向，限制兩個 QTextEdit 視窗寬度延伸
        self.diffWidget = QWidget()
        self.diffWidget.setLayout(self.diffHLayout)  # 設定水平佈局
        
        # 加入 tab 頁
        self.tabWidget.addTab(self.diffWidget, "Diff Line Result")
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.diffWidget), "行比對結果，" + 
        "\n滾輪：垂直卷軸 " +
        "\nAlt + 滾輪：水平卷軸 " +
        "\nShfit + 滾輪：兩邊垂直卷軸")

    def compareTexts(self):
        text1, text2 = self.textEdit1.toPlainText(), self.textEdit2.toPlainText()
        differ = Differ()
        diff = list(differ.compare(text1.splitlines(), text2.splitlines()))

        leftText, rightText = [], []

        for line in diff:
            if line.startswith('- '):
                leftText.append(line[2:])
                rightText.append('')
            elif line.startswith('+ '):
                leftText.append('')
                rightText.append(line[2:])
            elif line.startswith('  '):
                leftText.append(line[2:])
                rightText.append(line[2:])

        self.leftTextEdit.setPlainText('\n'.join(leftText))
        self.rightTextEdit.setPlainText('\n'.join(rightText))

        # 差異行色彩強調
        cursor1, cursor2 = self.leftTextEdit.textCursor(), self.rightTextEdit.textCursor()
        cursor1.movePosition(QTextCursor.Start)
        cursor2.movePosition(QTextCursor.Start)

        while not cursor1.atEnd() and not cursor2.atEnd():
            cursor1.movePosition(QTextCursor.StartOfBlock)
            cursor2.movePosition(QTextCursor.StartOfBlock)
            cursor1.select(QTextCursor.BlockUnderCursor)
            cursor2.select(QTextCursor.BlockUnderCursor)

            if cursor1.selectedText() != cursor2.selectedText():
                format1, format2 = QTextCharFormat(), QTextCharFormat()
                format1.setBackground(QColor('#FFC9C9'))
                format2.setBackground(QColor('#C9FFC9'))
                cursor1.mergeCharFormat(format1)
                cursor2.mergeCharFormat(format2)

            cursor1.movePosition(QTextCursor.NextBlock)
            cursor2.movePosition(QTextCursor.NextBlock)

        self.tabWidget.setTabEnabled(1, True)
        self.tabWidget.setCurrentWidget(self.diffWidget)

    def syncScroll(self, value):
        if QApplication.keyboardModifiers() == Qt.ShiftModifier:
            sender = self.sender()
            if sender == self.leftTextEdit.verticalScrollBar():
                self.rightTextEdit.verticalScrollBar().setValue(value)
            elif sender == self.rightTextEdit.verticalScrollBar():
                self.leftTextEdit.verticalScrollBar().setValue(value)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TextDiffApp()
    ex.show()
    sys.exit(app.exec_())
