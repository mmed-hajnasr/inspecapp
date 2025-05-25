import csv

import eel

eel.init("web")

data_type1 = "data/type1.csv"


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
    # Generate new nb (auto-increment)
    max_nb = max([int(row.get("nb", 0)) for row in csv_data], default=0)
    new_data["nb"] = str(max_nb + 1)

    # Ensure all required fields exist
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


@eel.expose
def data_pass(data):
    print("Received values: {}".format(str(data)))


if __name__ == "__main__":
    eel.start("index.html", mode="firefox", size=(1200, 800))
