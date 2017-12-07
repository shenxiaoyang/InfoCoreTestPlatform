# -*- coding:utf-8 -*-
from PyQt5.QtWidgets import *

#对话框-基础类型1
class BaseDlg1(QDialog):
    def __init__(self, parent=None):
        # super这个用法是调用父类的构造函数
        # parent=None表示默认没有父Widget，如果指定父亲Widget，则调用之
        super(BaseDlg1, self).__init__(parent)
        self.global_vars()
        self.init_ui()
        self.connect_all_signal_slot()

    def global_vars(self):
        self.x_left_margin_10 = 10  # x轴左边距10
        self.x_right_margin_10 = 10 # x轴右边距10
        self.y_up_margin_10 = 10    # y轴上边距10
        self.y_down_margin_10 =10   # y轴下边距10
        self.x_left_margin_2 = 2    # x轴左边距2
        self.x_right_margin_2 = 2   # x轴右边距2
        self.y_up_margin_2 = 2      # y轴上边距2
        self.y_down_margin_2 = 2    # y轴下边距2
        self.button_width_120 = 120 # 按钮宽度120
        self.button_width_80 = 80   # 按钮宽度80
        self.button_width_60 = 60   # 按钮宽度60
        self.button_width_50 = 50   # 按钮宽度50
        self.button_height_25 = 25  # 按钮高度25
        self.table_head_heigth = 28 # 表格表头行高
        self.table_row_heigth_25 = 25   #表行高25
        self.widget_heigth_space_5 = 5  #控件之间的高度间隙5
        self.widget_width_space_5 = 5   #控件之间的宽度间隙
        self.row_spacing_10 = 10  # 行间距
        self.col_spacing_10 = 10  # 列间距
        self.label_width_40 = 40
        self.label_heigth_25 = 25
        self.lineEdit_width_80 = 80
        self.lineEdit_width_20 = 20
        self.lineEdit_heigth_25 = 18

    def init_ui(self):
        pass

    def connect_all_signal_slot(self):
        pass

    def msg_success(self,msg_info):
        reply = QMessageBox.information(self,
                                        "结果",
                                        msg_info,
                                        QMessageBox.Yes)

    def msg_failed(self,msg_info):
        reply = QMessageBox.warning(self,
                                    "结果",
                                    msg_info,
                                    QMessageBox.Yes)