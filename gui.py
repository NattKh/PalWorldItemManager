from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QLineEdit, QPushButton, QLabel, QFileDialog, QInputDialog)
import json
import os
import sys

from parse_json import parse_json

class MainWindow(QMainWindow):
    def __init__(self, items):
        super().__init__()
        self.setWindowTitle("Item Manager")
        self.setGeometry(500, 500, 800, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout(self.central_widget)

        # Setup left and right layouts
        self.setup_left_layout(items)
        self.setup_right_layout()
        self.load_config()

    def setup_left_layout(self, items):
        self.left_layout = QVBoxLayout()
        self.main_layout.addLayout(self.left_layout, 1)

        self.all_items_label = QLabel("All Items List")
        self.left_layout.addWidget(self.all_items_label)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search Filter...")
        self.search_bar.textChanged.connect(self.filter_items)
        self.left_layout.addWidget(self.search_bar)

        self.available_items_list = QListWidget()
        self.items = items
        for item_name, description in items:
            QListWidgetItem(f"{item_name}: {description}", self.available_items_list)
        self.available_items_list.itemDoubleClicked.connect(self.move_item_to_pack)
        self.left_layout.addWidget(self.available_items_list)

    def setup_right_layout(self):
        self.right_layout = QVBoxLayout()
        self.main_layout.addLayout(self.right_layout, 1)
        self.set_path_button = QPushButton("Set Save Path")
        self.set_path_button.clicked.connect(self.set_save_path)
        self.right_layout.addWidget(self.set_path_button)
        self.path_display_label = QLabel("Save Path: Not set")
        self.right_layout.addWidget(self.path_display_label)

        self.picked_items_label = QLabel("Picked Items Your Items:")
        self.right_layout.addWidget(self.picked_items_label)

        self.item_picks_list = QListWidget()
        self.right_layout.addWidget(self.item_picks_list)
        self.edit_amount_button = QPushButton("Edit Amount")
        self.edit_amount_button.clicked.connect(self.edit_item_amount)
        self.right_layout.addWidget(self.edit_amount_button)

        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self.remove_selected_item)
        self.right_layout.addWidget(self.remove_button)

        self.remove_all_button = QPushButton("Remove All")
        self.remove_all_button.clicked.connect(self.remove_all_items)
        self.right_layout.addWidget(self.remove_all_button)

        #self.save_button = QPushButton("Save List")
        #self.save_button.clicked.connect(self.save_item_list)
        #self.right_layout.addWidget(self.save_button)
        # Inside setup_right_layout, add the button for saving as Lua
        self.save_lua_button = QPushButton("Save as Lua")
        self.save_lua_button.clicked.connect(self.save_item_list_as_lua)
        self.right_layout.addWidget(self.save_lua_button)

        #self.load_button = QPushButton("Load List")
        #self.load_button.clicked.connect(self.load_item_list)
        #self.right_layout.addWidget(self.load_button)
        self.load_lua_button = QPushButton("Load Lua")
        self.load_lua_button.clicked.connect(self.load_lua)
        self.right_layout.addWidget(self.load_lua_button)
    def load_config(self):
        try:
            with open('config.json', 'r') as config_file:
                config = json.load(config_file)
                self.save_path = config.get('save_path', '')
                self.path_display_label.setText(f"Save Path: {self.save_path}" if self.save_path else "Save Path: Not set")
        except FileNotFoundError:
            self.save_path = ''
            self.path_display_label.setText("Save Path: Not set")

    def set_save_path(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Save Directory")
        if dir_path:
            self.save_path = dir_path
            self.path_display_label.setText(f"Save Path: {dir_path}")  # Update label
            # Save the path to a config file
            with open('config.json', 'w') as config_file:
                json.dump({'save_path': dir_path}, config_file)


    def edit_item_amount(self):
        selected_items = self.item_picks_list.selectedItems()
        if selected_items:
            item = selected_items[0]  # single selection
            amount, ok = QInputDialog.getInt(self, "Edit Amount", f"Enter new amount for {item.text().split(':')[0]}:", min=1)
            if ok:
                item_name = item.text().split(':')[0]  # Extract item name without amount
                item.setText(f"{item_name}:{amount}")

    def load_lua(self):
        start_dir = self.save_path if self.save_path else ""  # Default to set path or current directory
        filename, _ = QFileDialog.getOpenFileName(self, "Load Lua File", start_dir, "Lua Files (*.lua)")
        if filename:
            with open(filename, 'r') as file:
                lua_content = file.read()

            # Simple parsing to extract item names from the Lua table
            item_names = self.parse_lua_content(lua_content)
            self.item_picks_list.clear()
            for name in item_names:
                # Find the description by matching the name in self.items
                for item, desc in self.items:
                    if item == name:
                        self.item_picks_list.addItem(f"{name}: {desc}")
                        break

    def parse_lua_content(self, lua_content):
        # A very basic parser to extract item names from the Lua table
        
        start = lua_content.find("{") + 1
        end = lua_content.find("}")
        lua_items = lua_content[start:end].split(',')
        item_names = [item.strip().strip('"') for item in lua_items]
        return item_names

    def filter_items(self):
        search_text = self.search_bar.text().lower()
        self.available_items_list.clear()  # Clear list for filtering

        # Re-populate list based on search
        for item_name, description in self.items:
            if search_text in item_name.lower() or search_text in description.lower():
                QListWidgetItem(f"{item_name}: {description}", self.available_items_list)

    def move_item_to_pack(self, item):
        # Debugging: Print the item text to the console
        print(f"Adding item to pack: {item.text()}")

        # Add item to player's picks list
        QListWidgetItem(item.text(), self.item_picks_list)
        # Remove item from available items list
        #self.available_items_list.takeItem(self.available_items_list.row(item))


    def remove_selected_item(self):
        for item in self.item_picks_list.selectedItems():
            self.item_picks_list.takeItem(self.item_picks_list.row(item))
    def remove_all_items(self):
        self.item_picks_list.clear()

    def save_item_list(self):
        list_name, ok = QInputDialog.getText(self, "Save List", "Enter list name:")
        if ok and list_name:
            filename = f"{list_name}_Give.json"
            items = [self.item_picks_list.item(i).text().split(': ')[1] for i in range(self.item_picks_list.count())]
            with open(filename, 'w') as file:
                json.dump(items, file)

    def save_item_list_as_lua(self):
        if not self.save_path:  # If no save path is set, prompt the user
            self.set_save_path() 
        if not self.save_path:  # Check again if the save path is still not set
            return  # Exit the function if no save path is set

        list_name, ok = QInputDialog.getText(self, "Save List as Lua", "Enter list name:")
        if ok and list_name:
            filename = os.path.join(self.save_path, f"{list_name}_Give.lua")

            # Construct the items list, including amounts if specified
            items = []
            for i in range(self.item_picks_list.count()):
                item_text = self.item_picks_list.item(i).text()
                item_parts = item_text.split(': ')
                item_name = item_parts[0]
                if len(item_parts) > 2:  # Format "ItemName: Description: Amount"
                    amount = item_parts[2]
                    items.append(f'"{item_name}:{amount}"')
                else:
                    items.append(f'"{item_name}"')

            # Construct the Lua table string
            lua_table = f"local {list_name} = {{\n    " + ",\n    ".join(items) + f"\n}}\n\nreturn {list_name}\n"

            
            # Save the Lua script to the file
            with open(filename, 'w') as file:
                file.write(lua_table)




    def load_item_list(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Load List", "", "JSON Files (*.json)")
        if filename:
            with open(filename, 'r') as file:
                items = json.load(file)
                self.item_picks_list.clear()
                for item in items:
                    QListWidgetItem(item, self.item_picks_list)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    file_path = 'DT_ItemNameText.json' 
    items = parse_json(file_path)

    window = MainWindow(items)
    window.show()

    sys.exit(app.exec_())
