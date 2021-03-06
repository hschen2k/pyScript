from PySide2.QtWidgets import QWidget, QLineEdit, QHBoxLayout, QVBoxLayout, QLabel, QMenu, QAction
from PySide2.QtGui import QIcon, QDrag, QPixmap
from PySide2.QtCore import Signal, QRect, QPoint, QMimeData, QByteArray, Qt, QEvent, QBuffer, QByteArray

import json

from custom_src.ListWidget_NameLineEdit import ListWidget_NameLineEdit
from custom_src.EditVarVal_Dialog import EditVarVal_Dialog


class VarsList_VarWidget(QWidget):

    name_le_editing_finished = Signal()

    def __init__(self, vars_list_widget, var):
        super(VarsList_VarWidget, self).__init__()

        self.var = var
        self.vars_list_widget = vars_list_widget

        self.ignore_name_line_edit_signal = False


        # UI
        main_layout = QHBoxLayout()

        # create icon via label
        variable_icon = QIcon('stuff/pics/variable_picture.png')
        icon_label = QLabel()
        icon_label.setFixedSize(15, 15)
        icon_label.setStyleSheet('border:none;')
        icon_label.setPixmap(variable_icon.pixmap(15, 15))
        main_layout.addWidget(icon_label)

        # create name and data_type line edits
        self.name_line_edit = ListWidget_NameLineEdit(var.name, self)
        self.name_line_edit.setPlaceholderText('name')
        # TODO create variable name and dt-type stylesheets
        #  (with small border/paddin/margin - this didn't work so far at all - I don't know why)
        #  Also the double click event on a line edit only get's catched correctly when clicking in the middle
        self.name_line_edit.setEnabled(False)
        self.name_line_edit.editingFinished.connect(self.name_line_edit_editing_finished)
        self.name_line_edit.unfocused.connect(self.name_line_edit_editing_finished)
        # TODO handle the variable name-and dt-line_edit's 'editing finished' the right way.
        #  It doesn't work when just clicking to somewhere else after starting to edit (it stays editable)

        name_type_layout = QVBoxLayout()
        name_type_layout.addWidget(self.name_line_edit)
        main_layout.addLayout(name_type_layout)

        # TODO create buttons (del, maybe: move up, move down etc.)

        # add whole layout to the main widget and save in widgets array
        self.setLayout(main_layout)



    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.name_line_edit.geometry().contains(event.pos()):
                self.name_line_edit_double_clicked()
                return


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            data_text = self.get_drag_data()
            data = QByteArray(bytes(data_text, 'utf-8'))
            mime_data.setData('text/plain', data)
            drag.setMimeData(mime_data)
            drop_action = drag.exec_()
            return


    def event(self, event):
        if event.type() == QEvent.ToolTip:
            val_str = ''
            try:
                val_str = str(self.var.val)
            except Exception as e:
                val_str = 'couldn\'t stringify value'
            self.setToolTip('val type: '+str(type(self.var.val))+'\nval: '+val_str)

        return QWidget.event(self, event)


    def contextMenuEvent(self, event):
        menu: QMenu = QMenu(self)

        delete_action = QAction('delete')
        delete_action.triggered.connect(self.action_delete_triggered)

        edit_value_action = QAction('edit value')
        edit_value_action.triggered.connect(self.action_edit_val_triggered)

        actions = [delete_action, edit_value_action]
        for a in actions:
            menu.addAction(a)

        menu.exec_(event.globalPos())


    def action_delete_triggered(self):
        self.vars_list_widget.del_variable(self.var, self)


    def action_edit_val_triggered(self):
        edit_var_val_dialog = EditVarVal_Dialog(self, self.var)
        accepted = edit_var_val_dialog.exec_()
        if accepted:
            self.var.val = edit_var_val_dialog.get_val()


    def name_line_edit_double_clicked(self):
        #line_edit: QLineEdit = self.sender()
        self.name_line_edit.setEnabled(True)
        self.name_line_edit.setFocus()
        self.name_line_edit.selectAll()

        self.vars_list_widget.currently_edited_var = self.var


    def get_drag_data(self):
        data = {'type': 'variable',
                'name': self.var.name,
                'value': self.var.val}  # value is probably unnecessary
        data_text = json.dumps(data)
        return data_text



    def name_line_edit_editing_finished(self):
        if self.ignore_name_line_edit_signal:
            return
        self.ignore_name_line_edit_signal = True
        self.name_le_editing_finished.emit()
        self.ignore_name_line_edit_signal = False