#!/usr/bin/env python3
import os
import sys
import subprocess
import json
import platform
import threading
from pathlib import Path

# Use PyQt5 instead of tkinter to avoid macOS version issues
try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QPushButton, QListWidget, QLabel, 
                                QFileDialog, QMessageBox, QMenu, QAction, QListWidgetItem,
                                QGraphicsDropShadowEffect, QSplitter, QFrame, QDialog, QComboBox,
                                QLineEdit, QTextEdit)
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve, QPoint, QTimer
    from PyQt5.QtGui import QIcon, QColor, QFont, QPixmap, QPalette, QBrush, QLinearGradient
except ImportError:
    print("PyQt5 is required. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt5"])
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QPushButton, QListWidget, QLabel, 
                                QFileDialog, QMessageBox, QMenu, QAction, QListWidgetItem,
                                QGraphicsDropShadowEffect, QSplitter, QFrame, QDialog, QComboBox,
                                QLineEdit, QTextEdit)
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve, QPoint, QTimer
    from PyQt5.QtGui import QIcon, QColor, QFont, QPixmap, QPalette, QBrush, QLinearGradient

# Import wine installer
try:
    from wine_installer import install_wine
except ImportError:
    def install_wine():
        print("Error: Wine installer not found")
        return False

class WineInstallerThread(QThread):
    finished = pyqtSignal(bool)
    
    def run(self):
        success = install_wine()
        self.finished.emit(success)

class StyledButton(QPushButton):
    def __init__(self, text, parent=None, primary=False):
        super().__init__(text, parent)
        self.primary = primary
        self.setFixedHeight(40)
        self.setFont(QFont("Arial", 11))
        
        # Apply shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)
        
        self.setCursor(Qt.PointingHandCursor)
        self.update_style()
    
    def update_style(self):
        if self.primary:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #5c2d91;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #7c3dbe;
                }
                QPushButton:pressed {
                    background-color: #4a2475;
                }
                QPushButton:disabled {
                    background-color: #cccccc;
                    color: #888888;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #f0f0f0;
                    color: #333333;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
                QPushButton:pressed {
                    background-color: #d0d0d0;
                }
                QPushButton:disabled {
                    background-color: #f5f5f5;
                    color: #aaaaaa;
                }
            """)

class ExeListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                padding: 5px;
            }
            QListWidget::item {
                height: 50px;
                border-radius: 6px;
                margin: 3px;
            }
            QListWidget::item:selected {
                background-color: #e6e0f0;
                color: #5c2d91;
            }
            QListWidget::item:hover {
                background-color: #f0f0f0;
            }
        """)
        
        # Apply shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

class WineExeManager(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set window properties
        self.setWindowTitle("Wine EXE Manager")
        self.setGeometry(100, 100, 1000, 700)
        self.setMinimumSize(900, 650)
        
        # Compatible apps library
        self.compatible_apps = {
            "Games": {
                "Balatro": {
                    "name": "Balatro",
                    "description": "A unique deck-building poker roguelike",
                    "compatibility": "Platinum",
                    "wine_version": "8.0 or later",
                    "notes": "Runs perfectly out of the box"
                },
                "Rocket League": {
                    "name": "Rocket League",
                    "description": "Soccer meets driving in this popular sports game",
                    "compatibility": "Gold",
                    "wine_version": "7.0 or later",
                    "notes": "Requires DirectX 11 and DXVK for best performance"
                }
            },
            "Productivity": {
                "Notepad++": {
                    "name": "Notepad++",
                    "description": "Popular text and code editor",
                    "compatibility": "Platinum",
                    "wine_version": "6.0 or later",
                    "notes": "Works perfectly with native file dialogs"
                }
            }
        }
        
        # App categories
        self.categories = {
            "Games": [],
            "Productivity": [],
            "Other": []
        }
        
        # Set app directory
        self.app_dir = os.path.dirname(os.path.abspath(__file__))
        self.wine_dir = os.path.join(self.app_dir, "wine")
        self.bottles_dir = os.path.join(self.app_dir, "bottles")
        self.exes_file = os.path.join(self.app_dir, "exes.json")
        
        # Create directories if they don't exist
        os.makedirs(self.wine_dir, exist_ok=True)
        os.makedirs(self.bottles_dir, exist_ok=True)
        
        # Load saved EXEs
        self.exes = self.load_exes()
        
        # Set application style
        self.set_application_style()
        
        # Create UI
        self.create_ui()
        
        # Check if Wine is installed
        self.check_wine()
        
    def set_application_style(self):
        # Set global application style with modern, Whiskey-like colors
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fb;
            }
            QStatusBar {
                background-color: #2d3436;
                color: white;
                padding: 8px;
                font-weight: 500;
                border-top: 1px solid #e0e0e0;
            }
            QSplitter::handle {
                background-color: #e8e9eb;
            }
            QLabel {
                color: #2d3436;
                font-size: 14px;
            }
            QFrame#sidebar {
                background-color: #2d3436;
                border-radius: 0px;
                margin: 0px;
            }
            QLabel#appTitle {
                color: white;
                font-size: 20px;
                font-weight: bold;
                padding: 20px 0px 5px 0px;
            }
            QLabel#appSubtitle {
                color: rgba(255, 255, 255, 0.7);
                font-size: 13px;
            }
            QPushButton {
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QListWidget {
                background-color: transparent;
                border: none;
                border-radius: 0px;
                padding: 8px;
            }
            QListWidget::item {
                background-color: white;
                border-radius: 8px;
                margin: 4px 8px;
                padding: 12px;
                min-height: 40px;
                border: 1px solid #e0e0e0;
            }
            QListWidget::item:selected {
                background-color: #f0f7ff;
                color: #2d3436;
                border: 1px solid #3498db;
            }
            QListWidget::item:hover {
                background-color: #f5f9ff;
                border: 1px solid #3498db;
            }
            QMenu {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 24px;
                border-radius: 4px;
                margin: 2px;
            }
            QMenu::item:selected {
                background-color: #f0f7ff;
                color: #2d3436;
            }
            QMenu::separator {
                height: 1px;
                background-color: #e0e0e0;
                margin: 4px 8px;
            }
        """)
        
    def load_exes(self):
        try:
            if os.path.exists(self.exes_file):
                with open(self.exes_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.exes = data.get('exes', [])
                        self.categories = data.get('categories', {
                            "Games": [],
                            "Productivity": [],
                            "Other": []
                        })
                    else:
                        # Handle old format where only exes were saved
                        self.exes = data
                        # Rebuild categories
                        self.categories = {
                            "Games": [],
                            "Productivity": [],
                            "Other": []
                        }
                        for i, exe in enumerate(self.exes):
                            category = exe.get("category", "Other")
                            if category not in self.categories:
                                self.categories[category] = []
                            self.categories[category].append(i)
                    return self.exes
            return []
        except Exception as e:
            error_msg = f"Error loading data: {str(e)}"
            print(error_msg)  # Print to console for debugging
            self.status_bar.showMessage(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
            return []
    
    def save_exes(self):
        try:
            # Ensure app directory exists
            os.makedirs(self.app_dir, exist_ok=True)
            
            # Create a backup of the existing file if it exists
            if os.path.exists(self.exes_file):
                backup_file = f"{self.exes_file}.bak"
                try:
                    import shutil
                    shutil.copy2(self.exes_file, backup_file)
                except Exception as e:
                    print(f"Warning: Could not create backup: {str(e)}")
            
            # Save the data
            with open(self.exes_file, 'w') as f:
                json.dump({
                    'exes': self.exes,
                    'categories': self.categories
                }, f, indent=2)
                
            self.status_bar.showMessage("Changes saved successfully")
            
        except Exception as e:
            error_msg = f"Error saving data: {str(e)}"
            print(error_msg)  # Print to console for debugging
            self.status_bar.showMessage(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
    
    def create_ui(self):
        # Create central widget with main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main horizontal layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 30, 20, 20)
        sidebar_layout.setSpacing(15)
        
        # Add app title to sidebar
        app_title = QLabel("Wine EXE Manager")
        app_title.setObjectName("appTitle")
        sidebar_layout.addWidget(app_title)
        
        # Add app subtitle
        app_subtitle = QLabel("Run Windows apps on macOS")
        app_subtitle.setObjectName("appSubtitle")
        sidebar_layout.addWidget(app_subtitle)
        
        sidebar_layout.addSpacing(30)
        
        # Add buttons to sidebar
        self.add_btn = StyledButton("Add EXE", primary=True)
        self.add_btn.clicked.connect(self.add_exe)
        sidebar_layout.addWidget(self.add_btn)
        
        self.refresh_btn = StyledButton("Refresh List")
        self.refresh_btn.clicked.connect(self.refresh_list)
        sidebar_layout.addWidget(self.refresh_btn)
        
        self.install_wine_btn = StyledButton("Install Wine")
        self.install_wine_btn.clicked.connect(self.download_wine)
        sidebar_layout.addWidget(self.install_wine_btn)
        
        sidebar_layout.addStretch(1)
        
        # Add version info at bottom of sidebar
        version_info = QLabel("Version 1.0")
        version_info.setStyleSheet("color: rgba(255, 255, 255, 0.5); font-size: 10px;")
        sidebar_layout.addWidget(version_info, alignment=Qt.AlignBottom)
        
        # Create content area
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(30, 30, 30, 30)
        
        # Add header
        header_layout = QHBoxLayout()
        header = QLabel("Your Windows Applications")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        header_layout.addWidget(header)
        content_layout.addLayout(header_layout)
        
        # Add instructions
        instructions = QLabel("Double-click an application to launch it, or right-click for more options.")
        instructions.setStyleSheet("color: #666; margin-bottom: 10px;")
        content_layout.addWidget(instructions)
        
        content_layout.addSpacing(10)
        
        # Create list widget for EXEs with custom styling
        self.exe_list = ExeListWidget()
        self.exe_list.itemDoubleClicked.connect(self.launch_selected)
        self.exe_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.exe_list.customContextMenuRequested.connect(self.show_context_menu)
        self.exe_list.setIconSize(QSize(32, 32))
        content_layout.addWidget(self.exe_list)
        
        # Add sidebar and content area to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_area)
        
        # Create status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
        
        # Populate list
        self.refresh_list()
        
        # Add animations with a slight delay
        QTimer.singleShot(100, self.animate_startup)
    
    def animate_startup(self):
        # Animate the sidebar buttons
        for i, button in enumerate([self.add_btn, self.refresh_btn, self.install_wine_btn]):
            button.setGraphicsEffect(None)  # Remove shadow temporarily for animation
            
            # Create opacity animation
            button.setStyleSheet("background-color: transparent; color: transparent; border: none;")
            
            # Use a timer to reset the style after animation
            QTimer.singleShot(400 + i * 100, lambda btn=button: self.reset_button_style(btn))
    
    def reset_button_style(self, button):
        button.update_style()
        
        # Re-apply shadow effect
        shadow = QGraphicsDropShadowEffect(button)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 3)
        button.setGraphicsEffect(shadow)
    
    def check_wine(self):
        # Check if bundled Wine exists
        wine_binary = self.find_wine_binary()
        if wine_binary:
            self.status_bar.showMessage(f"Using Wine at: {wine_binary}")
        else:
            reply = QMessageBox.question(
                self, 
                "Wine Not Found",
                "Wine is not installed. Would you like to download it now?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.download_wine()
            else:
                QMessageBox.information(
                    self,
                    "Wine Required",
                    "Wine is required to run Windows applications. The app will have limited functionality."
                )
    
    def find_wine_binary(self):
        """Find the Wine binary in our wine directory or the system"""
        # First check in our wine directory
        wine_bin_path = os.path.join(self.wine_dir, "bin", "wine")
        if os.path.exists(wine_bin_path) and os.access(wine_bin_path, os.X_OK):
            return wine_bin_path
            
        # Search recursively in the wine directory
        for root, dirs, files in os.walk(self.wine_dir):
            for file in files:
                if file == "wine":
                    file_path = os.path.join(root, file)
                    if os.access(file_path, os.X_OK):
                        return file_path
        
        # Check system wine as a last resort
        try:
            which_wine = subprocess.run(["which", "wine"], check=True, stdout=subprocess.PIPE, text=True)
            return which_wine.stdout.strip()
        except:
            return None
    
    def download_wine(self):
        """Download Wine in a separate thread to avoid blocking the UI"""
        self.status_bar.showMessage("Downloading Wine...")
        self.install_wine_btn.setEnabled(False)
        
        # Create and start the installer thread
        self.installer_thread = WineInstallerThread()
        self.installer_thread.finished.connect(self.download_wine_complete)
        self.installer_thread.start()
    
    def download_wine_complete(self, success):
        if success:
            self.status_bar.showMessage("Wine installed successfully")
            QMessageBox.information(self, "Success", "Wine has been installed successfully")
        else:
            self.status_bar.showMessage("Wine installation failed")
            QMessageBox.critical(self, "Error", "Failed to install Wine")
        
        self.install_wine_btn.setEnabled(True)
    
    def add_exe(self):
        try:
            print("DEBUG: Starting add_exe method")
            filepath, _ = QFileDialog.getOpenFileName(
                self,
                "Select EXE file",
                "",
                "EXE files (*.exe);;All files (*.*)"
            )
            print(f"DEBUG: Selected file: {filepath}")
            
            if not filepath:
                print("DEBUG: No file selected, returning")
                return
                
            # Get name for the application
            name = os.path.basename(filepath).replace(".exe", "")
            print(f"DEBUG: App name: {name}")
            
            # Show category selection dialog
            print("DEBUG: About to show category dialog")
            category = self.select_category_dialog(name)
            print(f"DEBUG: Selected category: {category}")
            
            if not category:  # User cancelled
                print("DEBUG: No category selected, returning")
                return
                
            # Create a bottle for this application
            bottle_name = f"bottle_{len(self.exes)}"
            bottle_path = os.path.join(self.bottles_dir, bottle_name)
            print(f"DEBUG: Creating bottle at: {bottle_path}")
            
            try:
                os.makedirs(bottle_path, exist_ok=True)
                print("DEBUG: Bottle directory created successfully")
            except Exception as e:
                print(f"DEBUG: Error creating bottle directory: {str(e)}")
                raise
            
            # Store app info with category
            exe_info = {
                "name": name,
                "path": filepath,
                "bottle": bottle_name,
                "category": category,
                "custom_name": name,
                "launch_options": "",
                "notes": ""
            }
            print(f"DEBUG: Created exe_info: {exe_info}")
            
            # Update categories and exes
            if category not in self.categories:
                print(f"DEBUG: Creating new category: {category}")
                self.categories[category] = []
            
            print(f"DEBUG: Current categories before update: {self.categories}")
            print(f"DEBUG: Current exes before update: {len(self.exes)}")
            
            self.exes.append(exe_info)
            new_index = len(self.exes) - 1
            self.categories[category].append(new_index)
            
            print(f"DEBUG: Added exe at index {new_index}")
            print(f"DEBUG: Updated categories: {self.categories}")
            
            # Save changes
            print("DEBUG: About to save changes")
            self.save_exes()
            print("DEBUG: Changes saved successfully")
            
            print("DEBUG: About to refresh list")
            self.refresh_list()
            print("DEBUG: List refreshed")
            
            # Show success message
            success_msg = f"Added {name} to {category}"
            print(f"DEBUG: {success_msg}")
            self.status_bar.showMessage(success_msg)
            
            # Find and select the new item
            print("DEBUG: Looking for new item to select")
            for i in range(self.exe_list.count()):
                item = self.exe_list.item(i)
                if item and item.data(Qt.UserRole) == new_index:
                    print(f"DEBUG: Found new item at position {i}")
                    item.setSelected(True)
                    self.animate_new_item(item)
                    break
            
            print("DEBUG: add_exe completed successfully")
                    
        except Exception as e:
            error_msg = f"Error adding EXE: {str(e)}"
            print(f"DEBUG: ERROR in add_exe: {error_msg}")
            print(f"DEBUG: Error type: {type(e)}")
            import traceback
            print(f"DEBUG: Traceback:\n{traceback.format_exc()}")
            self.status_bar.showMessage(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
    
    def animate_new_item(self, item):
        # Save original background
        original_style = item.data(Qt.UserRole) if item.data(Qt.UserRole) else ""
        
        # Highlight with animation
        item.setBackground(QColor("#e6f7ff"))
        
        # Use a timer to reset the background
        timer = QTimer(self)
        timer.singleShot(1000, lambda: item.setBackground(QColor("transparent")))
    
    def select_category_dialog(self, app_name):
        print(f"DEBUG: Starting select_category_dialog for {app_name}")
        try:
            # Check if app is in compatible apps list
            suggested_category = "Other"
            for category, apps in self.compatible_apps.items():
                if app_name in apps:
                    suggested_category = category
                    break
            
            print(f"DEBUG: Suggested category: {suggested_category}")
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Select Category")
            dialog.setModal(True)
            layout = QVBoxLayout()
            
            # Add category selection
            label = QLabel(f"Select category for {app_name}:")
            layout.addWidget(label)
            
            category_combo = QComboBox()
            for category in self.categories.keys():
                category_combo.addItem(category)
            
            # Set suggested category
            index = category_combo.findText(suggested_category)
            if index >= 0:
                category_combo.setCurrentIndex(index)
            
            layout.addWidget(category_combo)
            
            # Add buttons
            button_box = QHBoxLayout()
            ok_button = QPushButton("OK")
            ok_button.clicked.connect(dialog.accept)
            cancel_button = QPushButton("Cancel")
            cancel_button.clicked.connect(dialog.reject)
            button_box.addWidget(ok_button)
            button_box.addWidget(cancel_button)
            layout.addLayout(button_box)
            
            dialog.setLayout(layout)
            
            print("DEBUG: About to show category dialog")
            result = dialog.exec_()
            print(f"DEBUG: Dialog result: {result}")
            
            if result == QDialog.Accepted:
                selected_category = category_combo.currentText()
                print(f"DEBUG: Selected category: {selected_category}")
                return selected_category
            print("DEBUG: Dialog cancelled")
            return "Other"
            
        except Exception as e:
            print(f"DEBUG: Error in select_category_dialog: {str(e)}")
            import traceback
            print(f"DEBUG: Traceback:\n{traceback.format_exc()}")
            return "Other"
    
    def refresh_list(self):
        try:
            self.exe_list.clear()
            
            # Add category headers and apps
            for category in self.categories:
                # Add category header
                header_item = QListWidgetItem()
                header_item.setText(f"📁 {category}")
                header_item.setBackground(QColor("#f0f0f0"))
                header_item.setFlags(header_item.flags() & ~Qt.ItemIsSelectable)
                self.exe_list.addItem(header_item)
                
                # Add apps in this category
                category_apps = self.categories.get(category, [])
                for exe_index in category_apps:
                    if exe_index >= len(self.exes):
                        print(f"Warning: Invalid exe_index {exe_index} for category {category}")
                        continue
                        
                    exe = self.exes[exe_index]
                    item = QListWidgetItem()
                    
                    # Check if it's a known compatible app
                    is_compatible = False
                    if category in self.compatible_apps and exe["name"] in self.compatible_apps[category]:
                        is_compatible = True
                        app_info = self.compatible_apps[category][exe["name"]]
                        item.setToolTip(f"Compatibility: {app_info['compatibility']}\nWine Version: {app_info['wine_version']}\n{app_info['notes']}")
                    
                    # Set item text with compatibility indicator
                    display_name = exe.get("custom_name", exe["name"])
                    if is_compatible:
                        item.setText(f"✨ {display_name}")
                    else:
                        item.setText(display_name)
                    
                    item.setData(Qt.UserRole, exe_index)
                    self.exe_list.addItem(item)
                
                # Add spacing after category
                spacer = QListWidgetItem()
                spacer.setFlags(Qt.NoItemFlags)
                spacer.setSizeHint(QSize(0, 10))
                self.exe_list.addItem(spacer)
                
        except Exception as e:
            error_msg = f"Error refreshing list: {str(e)}"
            print(error_msg)  # Print to console for debugging
            self.status_bar.showMessage(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
    
    def get_wine_command(self):
        """Get the appropriate wine command"""
        wine_binary = self.find_wine_binary()
        if wine_binary:
            return wine_binary
        
        # If we can't find Wine, show an error
        QMessageBox.critical(self, "Error", "Wine is not installed. Please click 'Install Wine' first.")
        return None
    
    def launch_selected(self):
        selected_items = self.exe_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Select an EXE", "Please select an application to launch")
            return
            
        # Get the selected item's data
        exe_index = selected_items[0].data(Qt.UserRole)
        if exe_index is None:
            QMessageBox.information(self, "Select an EXE", "Please select a valid application")
            return
            
        exe_info = self.exes[exe_index]
        
        # Check if the file exists
        if not os.path.exists(exe_info["path"]):
            QMessageBox.critical(self, "Error", f"File not found: {exe_info['path']}")
            return
            
        # Launch with Wine
        wine_cmd = self.get_wine_command()
        if not wine_cmd:
            return
            
        bottle_path = os.path.join(self.bottles_dir, exe_info["bottle"])
        
        # Set WINEPREFIX to the bottle directory
        env = os.environ.copy()
        env["WINEPREFIX"] = bottle_path
        
        # Set DYLD_LIBRARY_PATH if we're using our bundled Wine
        if self.wine_dir in wine_cmd:
            wine_lib_dir = os.path.join(os.path.dirname(os.path.dirname(wine_cmd)), "lib")
            if os.path.exists(wine_lib_dir):
                env["DYLD_LIBRARY_PATH"] = wine_lib_dir
        
        # Build command with launch options
        cmd = [wine_cmd, exe_info["path"]]
        if exe_info.get("launch_options"):
            cmd.extend(exe_info["launch_options"].split())
        
        # Launch the EXE
        try:
            subprocess.Popen(cmd, env=env)
            self.status_bar.showMessage(f"Launched {exe_info.get('custom_name', exe_info['name'])}")
            
            # Visual feedback animation
            item = selected_items[0]
            original_bg = item.background()
            item.setBackground(QColor("#ebfbee"))  # Light green background
            
            # Reset background after animation
            timer = QTimer(self)
            timer.singleShot(1000, lambda: item.setBackground(original_bg))
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch {exe_info['name']}: {str(e)}")
    
    def show_context_menu(self, position):
        selected_items = self.exe_list.selectedItems()
        if not selected_items or not selected_items[0].data(Qt.UserRole):
            return
            
        context_menu = QMenu()
        context_menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 24px;
                border-radius: 4px;
                margin: 2px;
            }
            QMenu::item:selected {
                background-color: #f0e6f5;
                color: #8e44ad;
            }
            QMenu::separator {
                height: 1px;
                background-color: #e0e0e0;
                margin: 4px 8px;
            }
        """)
        
        # Get the selected exe
        exe_index = selected_items[0].data(Qt.UserRole)
        exe = self.exes[exe_index]
        
        # Create menu actions
        launch_action = QAction("🚀 Launch", self)
        launch_action.setIcon(QIcon.fromTheme("media-playback-start"))
        
        customize_action = QAction("✨ Customize", self)
        customize_action.setIcon(QIcon.fromTheme("preferences-system"))
        
        move_menu = QMenu("📁 Move to Category", self)
        for category in self.categories:
            if category != exe["category"]:
                action = QAction(category, self)
                action.triggered.connect(lambda checked, c=category: self.move_to_category(exe_index, c))
                move_menu.addAction(action)
        
        remove_action = QAction("🗑 Remove", self)
        remove_action.setIcon(QIcon.fromTheme("edit-delete"))
        
        # Add actions to menu
        context_menu.addAction(launch_action)
        context_menu.addAction(customize_action)
        context_menu.addMenu(move_menu)
        context_menu.addSeparator()
        context_menu.addAction(remove_action)
        
        # Show compatibility info if available
        if exe["category"] in self.compatible_apps and exe["name"] in self.compatible_apps[exe["category"]]:
            app_info = self.compatible_apps[exe["category"]][exe["name"]]
            info_action = QAction(f"ℹ️ {app_info['compatibility']} Compatibility", self)
            info_action.setEnabled(False)
            context_menu.insertAction(launch_action, info_action)
            context_menu.insertSeparator(launch_action)
        
        action = context_menu.exec_(self.exe_list.mapToGlobal(position))
        
        if action == launch_action:
            self.launch_selected()
        elif action == customize_action:
            self.customize_exe(exe_index)
        elif action == remove_action:
            self.remove_selected()
    
    def customize_exe(self, exe_index):
        exe = self.exes[exe_index]
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Customize {exe['name']}")
        dialog.setModal(True)
        layout = QVBoxLayout()
        
        # Display name
        name_layout = QHBoxLayout()
        name_label = QLabel("Display Name:")
        name_input = QLineEdit(exe.get("custom_name", exe["name"]))
        name_layout.addWidget(name_label)
        name_layout.addWidget(name_input)
        layout.addLayout(name_layout)
        
        # Launch options
        options_layout = QHBoxLayout()
        options_label = QLabel("Launch Options:")
        options_input = QLineEdit(exe.get("launch_options", ""))
        options_input.setPlaceholderText("Additional command line arguments")
        options_layout.addWidget(options_label)
        options_layout.addWidget(options_input)
        layout.addLayout(options_layout)
        
        # Notes
        notes_label = QLabel("Notes:")
        notes_input = QTextEdit(exe.get("notes", ""))
        notes_input.setPlaceholderText("Add your notes about this application")
        layout.addWidget(notes_label)
        layout.addWidget(notes_input)
        
        # Buttons
        button_box = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(dialog.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        button_box.addWidget(save_button)
        button_box.addWidget(cancel_button)
        layout.addLayout(button_box)
        
        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted:
            # Save customizations
            exe["custom_name"] = name_input.text()
            exe["launch_options"] = options_input.text()
            exe["notes"] = notes_input.toPlainText()
            self.save_exes()
            self.refresh_list()
    
    def move_to_category(self, exe_index, new_category):
        exe = self.exes[exe_index]
        old_category = exe["category"]
        
        # Remove from old category
        self.categories[old_category].remove(exe_index)
        
        # Add to new category
        self.categories[new_category].append(exe_index)
        exe["category"] = new_category
        
        self.save_exes()
        self.refresh_list()
        self.status_bar.showMessage(f"Moved {exe['name']} to {new_category}")
    
    def remove_selected(self):
        selected_items = self.exe_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Select an EXE", "Please select an EXE to remove")
            return
            
        selected_idx = self.exe_list.row(selected_items[0])
        exe_name = self.exes[selected_idx]["name"]
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Confirm Removal",
            f"Are you sure you want to remove {exe_name}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            del self.exes[selected_idx]
            self.save_exes()
            self.refresh_list()
            self.status_bar.showMessage(f"Removed {exe_name}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Use Fusion style for consistent look across platforms
    window = WineExeManager()
    window.show()
    sys.exit(app.exec_()) 