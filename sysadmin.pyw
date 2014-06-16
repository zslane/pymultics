import os
import sys
import cPickle as pickle
from pprint import pprint

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
        
        with open(filepath, "rb") as f:
            self.person_name_table = pickle.load(f) # <-- requires pnt module
        # end with
        self.person_ids = self.person_name_table.person_id_list()
        
    def rowCount(self, index=QtCore.QModelIndex()):
        return 0 if index.isValid() else len(self.person_ids)
        
    def columnCount(self, index=QtCore.QModelIndex()):
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
                
        return None

class SystemAdminTableUi(QtGui.QWidget):
    def __init__(self, filepath, parent=None):
        super(SystemAdminTableUi, self).__init__(parent)
        
        self.model = SystemAdminTableModel(filepath, self)
        
        self.projects_table_view = SystemAdminTableView()
        self.projects_table_view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.projects_table_view.setModel(self.model)
        for col in range(1, self.model.columnCount()):
            self.projects_table_view.resizeColumnToContents(col)
        
        main_layout = QtGui.QVBoxLayout()
        main_layout.addWidget(self.projects_table_view)
                
        self.setLayout(main_layout)
        
class SystemAdminTableView(QtGui.QTableView):
    def __init__(self, parent=None):
        super(SystemAdminTableView, self).__init__(parent)
        
class SystemAdminTableModel(QtCore.QAbstractTableModel):
    def __init__(self, filepath, parent=None):
        super(SystemAdminTableModel, self).__init__(parent)
        
        with open(filepath, "rb") as f:
            self.system_admin_table = pickle.load(f)
        # end with
                
        self.project_id_list = self.system_admin_table.projects.keys()
        
    def rowCount(self, index=QtCore.QModelIndex()):
        return 0 if index.isValid() else len(self.system_admin_table.projects)
        
    def columnCount(self, index=QtCore.QModelIndex()):
        return 0 if index.isValid() else 3
    
    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return ["Project Id", "Alias", "Admins"][section]
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
            project = self.system_admin_table.projects[self.project_id_list[row]]
            if col == 0:
                return project['project_id']
            elif col == 1:
                return project['alias']
            elif col == 2:
                return ", ".join(project['admins'])
                
        return None

class ProjectDefinitionTableUi(QtGui.QWidget):
    def __init__(self, filepath, parent=None):
        super(ProjectDefinitionTableUi, self).__init__(parent)
        
        self.model = ProjectDefinitionTableModel(filepath, self)
        
        self.users_table_view = ProjectUsersTableView()
        self.users_table_view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.users_table_view.setModel(self.model)
        for col in range(1, self.model.columnCount()):
            self.users_table_view.resizeColumnToContents(col)
        
        main_layout = QtGui.QVBoxLayout()
        main_layout.addWidget(self.users_table_view)
                
        self.setLayout(main_layout)
        
class ProjectUsersTableView(QtGui.QTableView):
    def __init__(self, parent=None):
        super(ProjectUsersTableView, self).__init__(parent)
        
class ProjectDefinitionTableModel(QtCore.QAbstractItemModel):
    def __init__(self, filepath, parent=None):
        super(ProjectDefinitionTableModel, self).__init__(parent)
        
        with open(filepath, "rb") as f:
            self.project_definition_table = pickle.load(f)
        # end with
        
        self.alias = self.project_definition_table.alias
        self.users = self.project_definition_table.users
        self.person_id_list = self.users.keys()
        
        # pprint(self.project_definition_table.users)
        
    def rowCount(self, index=QtCore.QModelIndex()):
        return 0 if index.isValid() else len(self.users)
        
    def columnCount(self, index=QtCore.QModelIndex()):
        return 0 if index.isValid() else 3
    
    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return ["Person Id", "Home Directory", "Command Processor"][section]
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
            user = self.users[self.person_id_list[row]]
            if col == 0:
                return user.person_id
            elif col == 1:
                return user.home_dir or "Default"
            elif col == 2:
                return user.cp_path or "Default"
                
        return None

class SysAdminWindow(QtGui.QMainWindow):
    def __init__(self):
        super(SysAdminWindow, self).__init__(None)
        
        self.setWindowTitle("System Admin Tool")
        self.set_up_menus()
        
        pnt_path = os.path.join(FILESYSTEMROOT, "sc1", "person_name_table")
        sat_path = os.path.join(FILESYSTEMROOT, "sc1", "system_administrator_table")
        
        self.pnt_ui = PersonNameTableUi(pnt_path)
        self.sat_ui = SystemAdminTableUi(sat_path)
        self.pdt_ui_list = []
        
        self.tab_widget = QtGui.QTabWidget(self)
        self.tab_widget.addTab(self.pnt_ui, "PNT")
        self.tab_widget.addTab(self.sat_ui, "SAT")
        
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
        pdt_path = os.path.join(FILESYSTEMROOT, "sc1")
        filepath, _ = QtGui.QFileDialog.getOpenFileName(self, "Open PDT File", pdt_path, "PDT Files (*.pdt)")
        if filepath:
            tab_title = os.path.basename(filepath)
            for i in range(self.tab_widget.count()):
                if tab_title == self.tab_widget.tabText(i):
                    self.tab_widget.setCurrentIndex(i)
                    break
                #end if
            else:
                pdt_ui = ProjectDefinitionTableUi(filepath)
                if pdt_ui.model.alias:
                    tab_title += " (%s)" % (pdt_ui.model.alias)
                # end if
                self.tab_widget.addTab(pdt_ui, tab_title)
                self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)
                self.pdt_ui_list.append(pdt_ui)
        
if __name__ == "__main__":
    app = QtGui.QApplication([])
    
    win = SysAdminWindow()
    win.show()
    
    app.exec_()
    