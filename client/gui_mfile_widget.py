import os.path

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, \
    QListWidgetItem, QSizePolicy
import json, socket

from gui_sec_filename_widget import SecFileNameWidget


class MFileWidget(QWidget):
    def __init__(self, client, parent=None):
        super(MFileWidget, self).__init__(parent)
        self.client = client
        self.personnel_files = []
        self.nuclear_files = []
        self.bio_files = []
        self.file_widgets = {
            "personnel_files": {},
            "nuclear_files": {},
            "bio_files": {}
        }

        self.l = QVBoxLayout()
        self.setLayout(self.l)
        self.label = QLabel("files",self)
        self.l.addWidget(self.label)
        self.widget = QWidget(self)
        self.l.addWidget(self.widget)
        self.vf_layout = QHBoxLayout()
        self.widget.setLayout(self.vf_layout)

        self.upload_files_button = QPushButton("Upload Files", self)
        self.upload_files_button.clicked.connect(self.upload_files)
        self.l.addWidget(self.upload_files_button)

        self.update_files_button = QPushButton("Update Files", self)
        self.update_files_button.clicked.connect(self.update_file_lists)
        self.l.addWidget(self.update_files_button)

        # self.print_files_button = QPushButton("print Files", self)
        # self.print_files_button.clicked.connect(self.print_files)
        # self.l.addWidget(self.print_files_button)

        self.personnel_list = QListWidget(self)
        self.nuclear_list = QListWidget(self)
        self.bio_list = QListWidget(self)

        self.vf_layout.addWidget(self.personnel_list)
        self.vf_layout.addWidget(self.nuclear_list)
        self.vf_layout.addWidget(self.bio_list)

        self.personnel_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.nuclear_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.bio_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        stylesheet = "QListWidget::item { padding: 0px; }"
        self.personnel_list.setStyleSheet(stylesheet)
        self.nuclear_list.setStyleSheet(stylesheet)
        self.bio_list.setStyleSheet(stylesheet)

        # self.personnel_scroll_area = QScrollArea()
        # self.personnel_scroll_area.setWidgetResizable(True)
        # #self.personnel_scroll_area.setMinimumHeight(300)
        # self.vf_layout.addWidget(self.personnel_scroll_area)
        # self.personnel_widget = QWidget()
        # self.personnel_scroll_area.setWidget(self.personnel_widget)
        # self.personnel_layout = QVBoxLayout()
        # self.personnel_widget.setLayout(self.personnel_layout)
        # self.personnel_layout.addStretch()
        #
        # self.nuclear_scroll_area = QScrollArea()
        # self.nuclear_scroll_area.setWidgetResizable(True)
        # #self.nuclear_scroll_area.setMinimumHeight(300)
        # self.vf_layout.addWidget(self.nuclear_scroll_area)
        # self.nuclear_widget = QWidget()
        # self.nuclear_scroll_area.setWidget(self.nuclear_widget)
        # self.nuclear_layout = QVBoxLayout()
        # self.nuclear_widget.setLayout(self.nuclear_layout)
        # self.nuclear_layout.addStretch()
        #
        # self.bio_scroll_area = QScrollArea()
        # self.bio_scroll_area.setWidgetResizable(True)
        # #self.bio_scroll_area.setMinimumHeight(300)
        # self.vf_layout.addWidget(self.bio_scroll_area)
        # self.bio_widget = QWidget()
        # self.bio_scroll_area.setWidget(self.bio_widget)
        # self.bio_layout = QVBoxLayout()
        # self.bio_widget.setLayout(self.bio_layout)
        # self.bio_layout.addStretch()


        self.vf_layout.addStretch()

        self.error_label = QLabel(self)
        self.error_label.setText("")
        self.vf_layout.addWidget(self.error_label)

    def update_file_lists(self):
        req_json = {
            'type': 'file_lists'
        }
        try:
            req = json.dumps(req_json)
            self.client.client_socket.send(req.encode())
        except Exception as e:
            print("Error: " + str(e))

        # looping = True
        # while looping:
        #     looping = False
        #
        #     try:
        #         rsp = self.client.client_socket.recv(1024).decode()
        #         rsp_json = json.loads(rsp)
        #         if rsp_json['type'] == 'file_lists':
        #             self.personnel_files = rsp_json['personnel_files']
        #             self.nuclear_files = rsp_json['nuclear_files']
        #             self.bio_files = rsp_json['bio_files']
        #         else:
        #             looping = True
        #     except socket.timeout:
        #         looping = True
        #     except Exception as e:
        #         print("Error: " + str(e))


    def show_files(self):
        self.clear_layouts()

        self.file_widgets['personnel_files'] = {}
        for filename in self.personnel_files:
            file = SecFileNameWidget(self.client, "personnel_files", filename, self, self.personnel_list)
            self.file_widgets["personnel_files"][filename] = file
            # self.personnel_layout.insertWidget(self.personnel_layout.count() - 1,file)
            item = QListWidgetItem()
            item.setSizeHint(file.sizeHint())
            self.personnel_list.addItem(item)
            self.personnel_list.setItemWidget(item, file)


        self.file_widgets['nuclear_files'] = {}
        for filename in self.nuclear_files:
            file = SecFileNameWidget(self.client, "nuclear_files", filename, self, self.nuclear_list)
            self.file_widgets["nuclear_files"][filename] = file
            # self.nuclear_layout.insertWidget(self.nuclear_layout.count() - 1, file)
            item = QListWidgetItem()
            item.setSizeHint(file.sizeHint())
            self.nuclear_list.addItem(item)
            self.nuclear_list.setItemWidget(item, file)



        self.file_widgets['bio_files'] = {}
        for filename in self.bio_files:
            file = SecFileNameWidget(self.client, "bio_files", filename, self, self.bio_list)
            self.file_widgets["bio_files"][filename] = file
            # self.bio_layout.insertWidget(self.bio_layout.count() - 1, file)
            item = QListWidgetItem()
            item.setSizeHint(file.sizeHint())
            self.bio_list.addItem(item)
            self.bio_list.setItemWidget(item, file)



    def clear_layouts(self):
        try:
            self.personnel_list.clear()
            self.nuclear_list.clear()
            self.bio_list.clear()
            for file_type in self.file_widgets:
                self.file_widgets[file_type].clear()
            # for file_type in self.file_widgets:
            #     for name in self.file_widgets[file_type]:
            #         print(name)
            #         self.file_widgets[file_type][name].hide()
            #         self.file_widgets[file_type][name].deleteLater()
        except Exception as e:
            print("Error in clear: " + str(e))

        # while layout.count():
        #     item = layout.takeAt(0)
        #     widget = item.widget()
        #     if widget is not None:
        #         layout.removeWidget(widget)
        #         widget.deleteLater()

    def upload_files(self):
        self.update_file_lists()
        req_json = {
            'type': 'update_files',
            'personnel_files': [],
            'nuclear_files': [],
            'bio_files': []
        }
        personnel_files = [f for f in os.listdir("files/personnel_files")]
        nuclear_files = [f for f in os.listdir("files/nuclear_files")]
        bio_files = [f for f in os.listdir("files/bio_files")]
        for filename in personnel_files:
            with open(f"files/personnel_files/{filename}", 'rb') as f:
                file_data = f.read()
            file_json = {
                'name': filename,
                'data': file_data.hex()
            }
            req_json['personnel_files'].append(file_json)

        for filename in nuclear_files:
            with open(f"files/nuclear_files/{filename}", 'rb') as f:
                file_data = f.read()
            file_json = {
                'name': filename,
                'data': file_data.hex()
            }
            req_json['nuclear_files'].append(file_json)

        for filename in bio_files:
            with open(f"files/bio_files/{filename}", 'rb') as f:
                file_data = f.read()
            file_json = {
                'name': filename,
                'data': file_data.hex()
            }
            req_json['bio_files'].append(file_json)
        req = json.dumps(req_json)
        self.client.client_socket.send(req.encode())


    def print_files(self):
        print(self.file_widgets)


    def show_error(self,msg):
        self.error_label.setText(msg)
        self.error_label.setStyleSheet("color: red")
    def show_message(self,msg):
        self.error_label.setText(msg)
        self.error_label.setStyleSheet("color: white")
