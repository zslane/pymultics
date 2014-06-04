import os
import sys
import cPickle as pickle

FILESYSTEMROOT = os.path.join(os.path.dirname(__file__), "multics", "filesystem")

system_includes_path = os.path.join(FILESYSTEMROOT, "sss", "includes")
if system_includes_path not in sys.path:
    sys.path.append(system_includes_path)
    
from pnt import *

from PySide import QtCore, QtGui

class PersonNameTableUi(QtGui.QWidget):
    def __init__(self, filepath, parent=None):
        super(PersonNameTableUi, self).__init__(parent)
        
        self.model = PersonNameTableModel(filepath, self)
        
        self.table_view = PersonNameTableView()
        self.table_view.setModel(self.model)
        
        main_layout = QtGui.QVBoxLayout()
        main_layout.addWidget(self.table_view)
        
        self.setLayout(main_layout)
        
class PersonNameTableView(QtGui.QTableView):
    def __init__(self, parent=None):
        super(PersonNameTableView, self).__init__(parent)
        
class PersonNameTableModel(QtCore.QAbstractTableModel):
    def __init__(self, filepath, parent=None):
        super(PersonNameTableModel, self).__init__(parent)
        
        with open(filepath, "r") as f:
            self.person_name_table = pickle.load(f) # <-- requires pnt module
        # end with
        self.person_ids = self.person_name_table.person_id_list()
        
    def rowCount(self, index):
        return 0 if index.isValid() else len(self.person_ids)
        
    def columnCount(self, index):
        return 0 if index.isValid() else 4
    
    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return ["Person Id", "Alias", "Default Project Id", "Has Password"][section]
            elif role == QtCore.Qt.TextAlignmentRole:
                return QtCore.Qt.AlignLeft
            # end if
        else:
            if role == QtCore.Qt.DisplayRole:
                return str(section + 1)
    
    def data(self, index, role):
        if not index.isValid():
            return None
            
        row = index.row()
        col = index.column()
        
        if role == QtCore.Qt.DisplayRole:
            name_entry = self.person_name_table.name_entries[self.person_ids[row]]
            if col == 0:
                return name_entry.person_id
            elif col == 1:
                return name_entry.alias
            elif col == 2:
                return name_entry.default_project_id
            elif col == 3:
                return "Yes" if name_entry.encrypted_password else "No"

class SysAdminWindow(QtGui.QMainWindow):
    def __init__(self):
        super(SysAdminWindow, self).__init__(None)
        
        self.set_up_menus()
        
        pnt_path = os.path.join(FILESYSTEMROOT, "sc1", "person_name_table")
        
        self.pnt_ui = PersonNameTableUi(pnt_path)
        
        self.tab_widget = QtGui.QTabWidget(self)
        self.tab_widget.addTab(self.pnt_ui, "PNT")
        
        self.setCentralWidget(self.tab_widget)
        
        self.resize(640, 480)
        
    def set_up_menus(self):
        file_menu = self.menuBar().addMenu("&File")
        
        open_action = file_menu.addAction("&Open Project Definition Table...")
        open_action.triggered.connect(self.open_pdt)
        
        file_menu.addSeparator()
        
        quit_action = file_menu.addAction("&Quit")
        quit_action.triggered.connect(self.close)
        
    @QtCore.Slot()
    def open_pdt(self):
        pass
        
if __name__ == "__main__":
    app = QtGui.QApplication([])
    
    pnt_path = os.path.join(os.path.dirname(__file__), "multics", "filesystem", "sc1", "person_name_table")
    
    win = SysAdminWindow()
    win.show()
    
    app.exec_()
    