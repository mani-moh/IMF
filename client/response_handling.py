import json
import socket
import threading

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QStackedWidget, QPushButton

from gui_tabs_widget import TabsWidget
from gui_viewfile_widget import ViewFileWidget

class ResponseSignals(QObject):
    show_files_signal = Signal()


class ResponseHandler(threading.Thread):
    def __init__(self, client_socket, client_instance):
        super().__init__(daemon=True)
        self.signals = ResponseSignals()
        self.client_socket = client_socket
        self.client = client_instance

        self.running = True
        # self.running = False

    def run(self):

        try:
            while self.running:
                try:
                    response_data = self.client_socket.recv(1024).decode()
                    try:
                        self.main_window.__str__()
                    except:
                        self.main_window = self.client.main_window
                    if response_data:
                        response = json.loads(response_data)
                        print(f"\nreceived response from server: {response}")
                        self.handle_response(response)
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"error while handling response1: {e}")
                    self.running = False
                except ConnectionResetError:
                    self.running = False
        except socket.timeout:
            print("socket timeout")
        except ConnectionResetError:
            print("connection reset error")
        except Exception as e:
            print(f"error while handling response2: {e}")

    def handle_response(self, response):

        match response["type"]:
            case 'server_closed':
                self.running = False
                self.client.running = False
            case 'login_result':
                if response["login_result"] == 'success':
                    print("\nlogin_successful\n>>>", end='')
                    self.client.data = response
                    self.client.logged_in = True
                    self.main_window.stacked_widget.start_page_widget.start_tabs_widget.login_page_button.hide()
                    self.main_window.stacked_widget.start_page_widget.start_tabs_widget.signup_page_button.hide()
                    self.main_window.stacked_widget.start_page_widget.start_tabs_widget.logout_page_button.show()
                    parent = self.main_window.stacked_widget.start_page_widget.start_stacked_widget
                    if isinstance(parent, QStackedWidget):
                        parent.setCurrentIndex(2)
                    tab = self.main_window.stacked_widget
                    if isinstance(tab, QStackedWidget):
                        self.main_window.tabs_widget.panel()
                        tab.setCurrentIndex(1)
                    panel_button = self.main_window.tabs_widget.panel_button
                    if isinstance(panel_button, QPushButton):
                        panel_button.show()
                    vf = self.main_window.stacked_widget.panel_widget.agent_panel.viewfile_tab
                    if isinstance(vf, ViewFileWidget):
                        vf.update_file_lists()
                else:
                    self.main_window.stacked_widget.start_page_widget.login_page.show_error(f"error: {response["login_result"]}")
                    # print('\n' + response["login_result"] + "\n>>>", end='')
            case 'signup_result':
                if response["signup_result"] == 'success':
                    # print("\nsignup_successful\n>>>", end='')
                    self.client.data = response
                    self.client.logged_in = True
                    self.main_window.stacked_widget.start_page_widget.start_tabs_widget.login_page_button.hide()
                    self.main_window.stacked_widget.start_page_widget.start_tabs_widget.signup_page_button.hide()
                    self.main_window.stacked_widget.start_page_widget.start_tabs_widget.logout_page_button.show()
                    parent = self.main_window.stacked_widget.start_page_widget.start_stacked_widget
                    if isinstance(parent, QStackedWidget):
                        parent.setCurrentIndex(2)
                    tab = self.main_window.stacked_widget
                    if isinstance(tab, QStackedWidget):
                        self.main_window.tabs_widget.panel()
                        tab.setCurrentIndex(1)
                    panel_button = self.main_window.tabs_widget.panel_button
                    if isinstance(panel_button, QPushButton):
                        panel_button.show()
                    vf = self.main_window.stacked_widget.panel_widget.agent_panel.viewfile_tab
                    if isinstance(vf, ViewFileWidget):

                        vf.update_file_lists()
                else:
                    self.main_window.stacked_widget.start_page_widget.signup_page.show_error(f"error: {response["signup_result"]}")

            case 'file_lists':
                if not (self.main_window.stacked_widget.panel_widget.agent_panel.viewfile_tab.personnel_files == response['personnel_files'] and
                    self.main_window.stacked_widget.panel_widget.agent_panel.viewfile_tab.nuclear_files == response['nuclear_files'] and
                    self.main_window.stacked_widget.panel_widget.agent_panel.viewfile_tab.bio_files == response['bio_files']):
                    pass
                    #todo check if same

                self.main_window.stacked_widget.panel_widget.agent_panel.viewfile_tab.personnel_files = response['personnel_files']
                self.main_window.stacked_widget.panel_widget.agent_panel.viewfile_tab.nuclear_files = response['nuclear_files']
                self.main_window.stacked_widget.panel_widget.agent_panel.viewfile_tab.bio_files = response['bio_files']
                self.signals.show_files_signal.emit()
                # self.main_window.stacked_widget.panel_widget.agent_panel.viewfile_tab.show_files()

            case 'file_data':
                file = self.main_window.stacked_widget.panel_widget.agent_panel.viewfile_tab.file_widgets[response['file_type']['file_name']]
                if response["status"] == 'success':
                    try:
                        with open(f"files/{file.file_type}/{file.filename}", 'wb') as f:
                            data = bytes.fromhex(response['data'])
                            f.write(data)
                            self.main_window.stacked_widget.panel_widget.agent_panel.viewfile_tab.show_message(f"downloaded {file.file_type}: {file.filename}")
                    except Exception as e:
                        self.main_window.stacked_widget.panel_widget.agent_panel.viewfile_tab.show_error(f"error: {e}")
                else:
                    self.main_window.stacked_widget.panel_widget.agent_panel.viewfile_tab.show_error(f"couldn't download file(server side)")
            case 'chat_message':
                pass

