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
                                QLineEdit, QTextEdit, QAbstractItemView, QScroller, QDrag, QMimeData)
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve, QPoint, QTimer
    from PyQt5.QtGui import QIcon, QColor, QFont, QPixmap, QPalette, QBrush, QLinearGradient, QPainter, QRect
except ImportError:
    print("PyQt5 is required. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt5"])
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QPushButton, QListWidget, QLabel, 
                                QFileDialog, QMessageBox, QMenu, QAction, QListWidgetItem,
                                QGraphicsDropShadowEffect, QSplitter, QFrame, QDialog, QComboBox,
                                QLineEdit, QTextEdit, QAbstractItemView, QScroller, QDrag, QMimeData)
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve, QPoint, QTimer
    from PyQt5.QtGui import QIcon, QColor, QFont, QPixmap, QPalette, QBrush, QLinearGradient, QPainter, QRect

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
    def __init__(self, text, primary=False, parent=None):
        super().__init__(text, parent)
        if primary:
            self.setProperty("primary", "true")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(36)

class ExeListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSpacing(4)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setViewMode(QListWidget.ListMode)
        self.setUniformItemSizes(False)
        self.setWordWrap(True)
        
        # Enable smooth scrolling
        scroller = QScroller.scroller(self.viewport())
        scroller.grabGesture(self.viewport(), QScroller.LeftMouseButtonGesture)
        scrollerProps = scroller.scrollerProperties()
        scrollerProps.setScrollMetric(QScrollerProperties.VerticalOvershootPolicy, QScrollerProperties.OvershootAlwaysOff)
        scroller.setScrollerProperties(scrollerProps)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if file_path.lower().endswith('.exe'):
                        self.parent().add_exe_file(file_path)
        else:
            event.ignore()

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if not item:
            return
            
        mimeData = QMimeData()
        mimeData.setText(item.text())
        
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        
        # Create a pixmap for drag visual
        pixmap = QPixmap(self.viewport().size())
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        option = self.viewOptions()
        option.rect = QRect(0, 0, pixmap.width(), item.sizeHint().height())
        self.itemDelegate().paint(painter, option, self.indexFromItem(item))
        painter.end()
        
        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(pixmap.width() / 2, pixmap.height() / 2))
        
        drag.exec_(supportedActions)

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
        # Set global application style with modern colors and styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fb;
            }
            QStatusBar {
                background-color: #ffffff;
                color: #1a1b1e;
                padding: 8px;
                font-weight: 500;
                border-top: 1px solid #e1e2e6;
            }
            QSplitter::handle {
                background-color: #e1e2e6;
            }
            QLabel {
                color: #1a1b1e;
                font-size: 14px;
            }
            QFrame#sidebar {
                background-color: #ffffff;
                border-right: 1px solid #e1e2e6;
                padding: 0px;
                margin: 0px;
            }
            QLabel#appTitle {
                color: #1a1b1e;
                font-size: 24px;
                font-weight: bold;
                padding: 20px;
            }
            QLabel#appSubtitle {
                color: #6b6c6f;
                font-size: 14px;
                padding-left: 20px;
                padding-right: 20px;
            }
            QPushButton {
                background-color: #ffffff;
                color: #1a1b1e;
                border: 1px solid #e1e2e6;
                border-radius: 8px;
                padding: 12px;
                font-weight: 500;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #f8f9fb;
                border-color: #d1d2d6;
            }
            QPushButton:pressed {
                background-color: #e1e2e6;
            }
            QPushButton[primary="true"] {
                background-color: #007AFF;
                color: white;
                border: none;
            }
            QPushButton[primary="true"]:hover {
                background-color: #0066FF;
            }
            QPushButton[primary="true"]:pressed {
                background-color: #0055FF;
            }
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #e1e2e6;
                border-radius: 12px;
                padding: 8px;
            }
            QListWidget::item {
                background-color: #ffffff;
                border-radius: 8px;
                margin: 4px;
                padding: 12px;
                min-height: 44px;
            }
            QListWidget::item:selected {
                background-color: #f0f7ff;
                color: #007AFF;
                border: 1px solid #007AFF;
            }
            QListWidget::item:hover:!selected {
                background-color: #f8f9fb;
            }
            QMenu {
                background-color: #ffffff;
                border: 1px solid #e1e2e6;
                border-radius: 8px;
                padding: 8px;
            }
            QMenu::item {
                padding: 8px 24px;
                border-radius: 6px;
                margin: 2px;
            }
            QMenu::item:selected {
                background-color: #f0f7ff;
                color: #007AFF;
            }
            QMenu::separator {
                height: 1px;
                background-color: #e1e2e6;
                margin: 4px 8px;
            }
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #e1e2e6;
                border-radius: 8px;
                padding: 8px;
                min-height: 20px;
            }
            QComboBox:hover {
                border-color: #d1d2d6;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #e1e2e6;
                border-radius: 8px;
                padding: 8px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border-color: #007AFF;
            }
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #e1e2e6;
                border-radius: 8px;
                padding: 8px;
            }
            QTextEdit:focus {
                border-color: #007AFF;
            }
        """)
        
    def load_exes(self):
        if os.path.exists(self.exes_file):
            try:
                with open(self.exes_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_exes(self):
        with open(self.exes_file, 'w') as f:
            json.dump(self.exes, f)
    
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
        sidebar.setFixedWidth(280)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 20)
        sidebar_layout.setSpacing(8)
        
        # Add app title to sidebar
        app_title = QLabel("Wine EXE Manager")
        app_title.setObjectName("appTitle")
        sidebar_layout.addWidget(app_title)
        
        # Add app subtitle
        app_subtitle = QLabel("Run Windows apps on macOS")
        app_subtitle.setObjectName("appSubtitle")
        sidebar_layout.addWidget(app_subtitle)
        
        sidebar_layout.addSpacing(20)
        
        # Create button container with padding
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setContentsMargins(20, 0, 20, 0)
        button_layout.setSpacing(8)
        
        # Add buttons to container
        self.add_btn = StyledButton("Add Windows Application", primary=True)
        self.add_btn.clicked.connect(self.add_exe)
        button_layout.addWidget(self.add_btn)
        
        self.refresh_btn = StyledButton("Refresh List")
        self.refresh_btn.clicked.connect(self.refresh_list)
        button_layout.addWidget(self.refresh_btn)
        
        self.install_wine_btn = StyledButton("Install Wine")
        self.install_wine_btn.clicked.connect(self.download_wine)
        button_layout.addWidget(self.install_wine_btn)
        
        sidebar_layout.addWidget(button_container)
        sidebar_layout.addStretch(1)
        
        # Add version info at bottom of sidebar
        version_info = QLabel("Version 1.0")
        version_info.setStyleSheet("color: #6b6c6f; font-size: 12px; padding: 0 20px;")
        sidebar_layout.addWidget(version_info, alignment=Qt.AlignBottom)
        
        # Create content area
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(16)
        
        # Add header
        header = QLabel("Your Applications")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #1a1b1e;")
        content_layout.addWidget(header)
        
        # Add instructions
        instructions = QLabel("Double-click an application to launch it, or right-click for more options.")
        instructions.setStyleSheet("color: #6b6c6f; margin-bottom: 16px;")
        content_layout.addWidget(instructions)
        
        # Create list widget for EXEs
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
        # Fade in animation for the window
        self.setWindowOpacity(0)
        animation = QPropertyAnimation(self, b"windowOpacity")
        animation.setDuration(500)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.start()
        
        # Slide in animation for sidebar items
        for i in range(self.sidebar.layout().count()):
            widget = self.sidebar.layout().itemAt(i).widget()
            if widget:
                pos = widget.pos()
                widget.move(pos.x() - 50, pos.y())
                anim = QPropertyAnimation(widget, b"pos")
                anim.setDuration(600)
                anim.setStartValue(QPoint(pos.x() - 50, pos.y()))
                anim.setEndValue(QPoint(pos.x(), pos.y()))
                anim.setEasingCurve(QEasingCurve.OutCubic)
                anim.setDelay(i * 50)  # Stagger the animations
                anim.start()
        
        # Scale up animation for content
        content = self.centralWidget().layout().itemAt(1).widget()
        content.setGeometry(content.x(), content.y(), content.width() * 0.95, content.height() * 0.95)
        anim = QPropertyAnimation(content, b"geometry")
        anim.setDuration(600)
        anim.setStartValue(content.geometry())
        anim.setEndValue(QRect(content.x(), content.y(), content.width() / 0.95, content.height() / 0.95))
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.setDelay(300)
        anim.start()
    
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
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Select EXE file",
            "",
            "EXE files (*.exe);;All files (*.*)"
        )
        
        if not filepath:
            return
            
        # Get name for the application
        name = os.path.basename(filepath).replace(".exe", "")
        
        # Show category selection dialog
        category = self.select_category_dialog(name)
        
        # Create a bottle for this application
        bottle_name = f"bottle_{len(self.exes)}"
        bottle_path = os.path.join(self.bottles_dir, bottle_name)
        os.makedirs(bottle_path, exist_ok=True)
        
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
        
        self.exes.append(exe_info)
        self.categories[category].append(len(self.exes) - 1)
        self.save_exes()
        self.refresh_list()
        self.status_bar.showMessage(f"Added {name} to {category}")
        
        # Animate the new item
        last_item = self.exe_list.item(self.exe_list.count() - 1)
        last_item.setSelected(True)
        self.animate_new_item(last_item)
    
    def animate_new_item(self, item):
        # Save original background
        original_style = item.data(Qt.UserRole) if item.data(Qt.UserRole) else ""
        
        # Highlight with animation
        item.setBackground(QColor("#e6f7ff"))
        
        # Use a timer to reset the background
        timer = QTimer(self)
        timer.singleShot(1000, lambda: item.setBackground(QColor("transparent")))
    
    def select_category_dialog(self, app_name):
        # Check if app is in compatible apps list
        suggested_category = "Other"
        for category, apps in self.compatible_apps.items():
            if app_name in apps:
                suggested_category = category
                break
        
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
        
        if dialog.exec_() == QDialog.Accepted:
            return category_combo.currentText()
        return "Other"
    
    def refresh_list(self):
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
            for exe_index in self.categories[category]:
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
            
        # Get the selected item's exe_index from UserRole data
        exe_index = selected_items[0].data(Qt.UserRole)
        if exe_index is None:
            return  # This is a category header or spacer
            
        exe_info = self.exes[exe_index]
        
        # Check if the file exists
        if not os.path.exists(exe_info["path"]):
            QMessageBox.critical(self, "Error", f"File not found: {exe_info['path']}\nThe file may have been moved or deleted.")
            return
            
        # Launch with Wine
        wine_cmd = self.get_wine_command()
        if not wine_cmd:
            return
            
        bottle_path = os.path.join(self.bottles_dir, exe_info["bottle"])
        
        # Ensure bottle directory exists
        os.makedirs(bottle_path, exist_ok=True)
        
        # Set environment variables
        env = os.environ.copy()
        env["WINEPREFIX"] = bottle_path
        
        # Set DYLD_LIBRARY_PATH if using bundled Wine
        if self.wine_dir in wine_cmd:
            wine_lib_dir = os.path.join(os.path.dirname(os.path.dirname(wine_cmd)), "lib")
            if os.path.exists(wine_lib_dir):
                env["DYLD_LIBRARY_PATH"] = wine_lib_dir
        
        # Build command with launch options
        cmd = [wine_cmd, exe_info["path"]]
        if exe_info.get("launch_options"):
            cmd.extend(exe_info["launch_options"].split())
        
        try:
            # Show launch status
            self.status_bar.showMessage(f"Launching {exe_info.get('custom_name', exe_info['name'])}...")
            
            # Launch the EXE
            process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Check if process started successfully
            if process.poll() is None:
                self.status_bar.showMessage(f"Launched {exe_info.get('custom_name', exe_info['name'])} successfully")
                
                # Visual feedback animation
                item = selected_items[0]
                original_bg = item.background()
                item.setBackground(QColor("#d1f7c4"))  # Green background
                
                # Reset background after animation
                timer = QTimer(self)
                timer.singleShot(1000, lambda: item.setBackground(original_bg))
            else:
                stdout, stderr = process.communicate()
                error_msg = stderr.decode() if stderr else "Unknown error"
                QMessageBox.critical(self, "Launch Error", 
                    f"Failed to launch {exe_info['name']}.\nError: {error_msg}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                f"Failed to launch {exe_info['name']}:\n{str(e)}\n\nPlease check if Wine is installed correctly.")
    
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