import csv
import eel
import os
import shutil
import base64
from pathlib import Path

eel.init("web")

# Ensure images directory exists
Path("web/data/images").mkdir(parents=True, exist_ok=True)

data_type1 = "web/data/type1.csv"


# Load CSV data
def load_csv_data():
    data = []
    try:
        with open(data_type1, "r", encoding="utf-8") as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                data.append(row)
    except FileNotFoundError:
        print("CSV file not found. Creating empty CSV file...")
        # Create empty CSV file with headers
        create_empty_csv()
        data = []
    return data


def create_empty_csv():
    """Create an empty CSV file with headers"""
    fieldnames = [
        "nb",
        "surname",
        "name",
        "date_of_issue",
        "date_of_expiry",
        "id",
        "MED",
        "LIC",
        "ATO",
        "TRTO",
        "FSTD",
        "MA",
        "GN",
        "AO",
        "RANPF",
        "RANPN",
    ]
    try:
        with open(data_type1, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
        print("Empty CSV file created successfully.")
    except Exception as e:
        print(f"Error creating CSV file: {e}")


# Store data in memory
csv_data = load_csv_data()


@eel.expose
def get_table_data():
    """Return table data for DataTable"""
    return csv_data


@eel.expose
def get_row_data(row_index):
    """Get data for a specific row"""
    global csv_data
    if 0 <= row_index < len(csv_data):
        return csv_data[row_index]
    return None


@eel.expose
def update_row(row_index, updated_data):
    """Update a specific row"""
    global csv_data
    if 0 <= row_index < len(csv_data):
        # Handle image if present
        if 'image' in updated_data:
            image_data = updated_data.pop('image')
            if image_data:
                # Get the inspector ID
                inspector_id = updated_data.get('id', csv_data[row_index]['id'])
                # Save the base64 image data
                target_path = f'web/data/images/{inspector_id}.png'
                try:
                    # Remove data URL prefix if present
                    if 'base64,' in image_data:
                        image_data = image_data.split('base64,')[1]
                    # Decode and save the image
                    image_bytes = base64.b64decode(image_data)
                    with open(target_path, 'wb') as f:
                        f.write(image_bytes)
                except Exception as e:
                    print(f'Error saving image: {e}')
        
        csv_data[row_index].update(updated_data)
        save_csv_data()
        return True
    return False


@eel.expose
def delete_row(row_index):
    """Delete a specific row"""
    global csv_data
    if 0 <= row_index < len(csv_data):
        del csv_data[row_index]
        save_csv_data()
        return True
    return False


@eel.expose
def add_new_row(new_data):
    """Add a new row"""
    global csv_data
    required_fields = [
        "nb",
        "surname",
        "name",
        "date_of_issue",
        "date_of_expiry",
        "id",
        "MED",
        "LIC",
        "ATO",
        "TRTO",
        "FSTD",
        "MA",
        "GN",
        "AO",
        "RANPF",
        "RANPN",
    ]
    # Handle image if present
    if 'image' in new_data:
        image_data = new_data.pop('image')
        if image_data:
            # Get the inspector ID
            inspector_id = new_data.get('id', '')
            if inspector_id:
                # Save the base64 image data
                target_path = f'web/data/images/{inspector_id}.png'
                try:
                    # Remove data URL prefix if present
                    if 'base64,' in image_data:
                        image_data = image_data.split('base64,')[1]
                    # Decode and save the image
                    image_bytes = base64.b64decode(image_data)
                    with open(target_path, 'wb') as f:
                        f.write(image_bytes)
                except Exception as e:
                    print(f'Error saving image: {e}')
    
    for field in required_fields:
        if field not in new_data:
            new_data[field] = ""

    csv_data.append(new_data)
    save_csv_data()
    return True


def save_csv_data():
    """Save data back to CSV file"""
    try:
        fieldnames = [
            "nb",
            "surname",
            "name",
            "date_of_issue",
            "date_of_expiry",
            "id",
            "MED",
            "LIC",
            "ATO",
            "TRTO",
            "FSTD",
            "MA",
            "GN",
            "AO",
            "RANPF",
            "RANPN",
        ]
        with open(data_type1, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_data)
    except Exception as e:
        print(f"Error saving CSV: {e}")

if __name__ == "__main__":
    eel.start("index.html", mode="firefox", size=(1200, 800))
