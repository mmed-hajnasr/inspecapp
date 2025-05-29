import base64
import csv
import os
from pathlib import Path

import eel
from PIL import Image, ImageDraw, ImageFont

# Initialize eel with the web files
web_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
eel.init(web_path)

# Ensure images directory exists
Path(os.path.join(web_path, "data", "images")).mkdir(parents=True, exist_ok=True)
Path(os.path.join(web_path, "output")).mkdir(parents=True, exist_ok=True)

# Set data path
data_path = os.path.join(web_path, "data", "inspectors.csv")
output_path = os.path.join(web_path, "output")
front_path = os.path.join(output_path, "front.png")
back_path = os.path.join(output_path, "back.png")


# Load CSV data
def load_csv_data():
    data = []
    try:
        with open(data_path, "r", encoding="utf-8") as file:
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
        "type",
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
        "INFR",
        "AIDs",
        "SSLIA",
        "ATS",
        "MET",
        "AIS/AIM",
        "SAR",
        "PANS-OPS",
        "MAP",
        "CNS",
    ]
    try:
        with open(data_path, "w", newline="", encoding="utf-8") as file:
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
        if "image" in updated_data:
            image_data = updated_data.pop("image")
            if image_data:
                # Get the inspector ID
                inspector_id = updated_data.get("id", csv_data[row_index]["id"])
                # Save the base64 image data
                target_path = f"web/data/images/{inspector_id}.png"
                try:
                    # Remove data URL prefix if present
                    if "base64," in image_data:
                        image_data = image_data.split("base64,")[1]
                    # Decode and save the image
                    image_bytes = base64.b64decode(image_data)
                    with open(target_path, "wb") as f:
                        f.write(image_bytes)
                except Exception as e:
                    print(f"Error saving image: {e}")

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
def save_sig_image(image_data):
    try:
        if (
            not image_data
            or not isinstance(image_data, dict)
            or "image" not in image_data
        ):
            print("Invalid or empty image data")
            return {"success": False}

        image_base64 = image_data["image"]
        # Remove data URL prefix if present
        if "base64," in image_base64:
            image_base64 = image_base64.split("base64,")[1]

        # Decode and save the image
        image_bytes = base64.b64decode(image_base64)
        target_path = "web/data/images/signature.png"

        with open(target_path, "wb") as f:
            f.write(image_bytes)

        return {"success": True}
    except Exception as e:
        print(f"Error saving signature image: {e}")
        return {"success": False}


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
    if "image" in new_data:
        image_data = new_data.pop("image")
        if image_data:
            # Get the inspector ID
            inspector_id = new_data.get("id", "")
            if inspector_id:
                # Save the base64 image data
                target_path = f"web/data/images/{inspector_id}.png"
                try:
                    # Remove data URL prefix if present
                    if "base64," in image_data:
                        image_data = image_data.split("base64,")[1]
                    # Decode and save the image
                    image_bytes = base64.b64decode(image_data)
                    with open(target_path, "wb") as f:
                        f.write(image_bytes)
                except Exception as e:
                    print(f"Error saving image: {e}")

    for field in required_fields:
        if field not in new_data:
            new_data[field] = ""

    csv_data.append(new_data)
    save_csv_data()
    return True


@eel.expose
def print_card(row_index):
    print_front(row_index)
    print_back(row_index)


def print_front(row_index):
    template_path = "templates/front.png"
    data = get_row_data(row_index)

    image = Image.open(template_path)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("./ARIAL.TTF", 30)
    photo_path = "web/data/images/" + data["id"] + ".png"
    signature_path = "web/data/images/signature.png"

    if photo_path:
        try:
            photo = Image.open(photo_path)
            photo = photo.resize((200, 190))
            image.paste(photo, (40, 180))
        except Exception as e:
            print(f"Error adding photo: {e}")

    if signature_path:
        try:
            photo = Image.open(signature_path)
            photo = photo.resize((280, 120))
            image.paste(photo, (20, 380))
        except Exception as e:
            print(f"Error adding signature: {e}")

    # Text positions (adjust these based on your template)
    positions = {
        "nb": (570, 245),
        "surname": (480, 295),
        "name": (430, 335),
        "date_of_issue": (550, 370),
        "date_of_expiry": (550, 410),
        "id": (380, 445),
    }

    # Fill the fields
    for field, position in positions.items():
        if field in data:
            draw.text(position, str(data[field]), fill=(0, 0, 0), font=font)

    # Save
    image.save(front_path)
    print(f"front card saved to: {front_path}")


def print_back(row_index):
    """Fill the qualifications table card"""
    # Sample qualifications data (X = checked, empty = unchecked)
    data = get_row_data(row_index)
    inspector_type = int(data["type"])
    if inspector_type == 1:
        template_path = "templates/PEL-AIR-OPS.png"
        x = 190
        y = 280
        step = 65
    elif inspector_type == 2:
        template_path = "templates/AGA.png"
        x = 310
        y = 275
        step = 190
    elif inspector_type == 3:
        template_path = "templates/ANS.png"
        x = 225
        y = 325
        step = 110
    else:
        raise TypeError("type needs to be 1 to 3")

    qualifications = [
        [],
        ["MED", "LIC", "ATO", "TRTO", "FSTD", "MA", "GN", "AO", "RANPF", "RANPN"],
        ["INFR", "AIDs", "SSLIA"],
        ["ATS", "MET", "AIS/AIM", "SAR", "PANS-OPS", "MAP", "CNS"],
    ]

    # Load image
    image = Image.open(template_path)
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype("./ARIAL.TTF", 60)

    positions = {}
    for qualification in qualifications[inspector_type]:
        positions[qualification] = (x, y)
        x += step

    # Fill qualifications
    for qual, position in positions.items():
        draw.text(position, data[qual], fill=(0, 0, 0), font=font)

    # Save
    image.save(back_path)
    print(f"back card saved to: {back_path}")


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
            "type",
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
            "INFR",
            "AIDs",
            "SSLIA",
            "ATS",
            "MET",
            "AIS/AIM",
            "SAR",
            "PANS-OPS",
            "MAP",
            "CNS",
        ]
        with open(data_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_data)
    except Exception as e:
        print(f"Error saving CSV: {e}")


if __name__ == "__main__":
    eel.start("index.html", mode="default", size=(1200, 800))
