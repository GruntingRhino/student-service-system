import csv
import re
import os

seen = set()
duplicates = []

def is_row_corrupted(row, row_number=None):
    """
    Checks if a CSV row is corrupted.
    
    Args:
        row (list): The CSV row to check
        row_number (int, optional): Row number for error reporting
    
    Returns:
        tuple: (is_corrupted: bool, error_message: str)
    """
    row_info = f"Row {row_number}" if row_number is not None else "Row"
    
    # Check if row has enough columns
    if len(row) < 4:
        return True, f"{row_info}: Missing columns (expected 4, found {len(row)})"
    
    # Check if required fields are empty
    name = row[0].strip() if row[0] else ""
    date = row[1].strip() if row[1] else ""
    hours_str = row[2].strip() if row[2] else ""
    status = row[3].strip() if row[3] else ""
    
    if not name:
        return True, f"{row_info}: Missing or empty student name"
    
    if not date:
        return True, f"{row_info}: Missing or empty date"
    
    if not hours_str:
        return True, f"{row_info}: Missing or empty hours"
    
    if not status:
        return True, f"{row_info}: Missing or empty status"
    
    # Validate date format
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date):
        return True, f"{row_info}: Invalid date format '{date}' (expected YYYY-MM-DD)"
    
    # Validate hours is a number and positive
    try:
        hours = float(hours_str)
        if hours < 0:
            return True, f"{row_info}: Hours cannot be negative ({hours})"
    except ValueError:
        return True, f"{row_info}: Invalid hours value '{hours_str}' (must be a number)"
    
    # Validate status is 'true' or 'false'
    status_lower = status.lower()
    if status_lower not in ['true', 'false']:
        return True, f"{row_info}: Invalid status '{status}' (must be 'true' or 'false')"
    
    return False, ""

def check_for_corrupted_rows(filename='service_hours.csv'):
    """
    Checks the CSV file for corrupted rows and reports them.
    
    Args:
        filename (str): Name of the CSV file to check
    
    Returns:
        list: List of tuples (row_number, error_message) for corrupted rows
    """
    corrupted_rows = []
    
    try:
        if not os.path.exists(filename):
            print(f"{filename} not found.")
            return corrupted_rows
        
        with open(filename, 'r', newline='') as file:
            reader = csv.reader(file)
            for row_number, row in enumerate(reader, start=1):
                is_corrupted, error_msg = is_row_corrupted(row, row_number)
                if is_corrupted:
                    corrupted_rows.append((row_number, error_msg))
                    print(f"Corrupted {error_msg}: {row}")
    
    except Exception as e:
        print(f"Error checking {filename} for corrupted rows: {e}")
    
    return corrupted_rows

def create_total_hours_csv():
    student_hours = {}
    
    # Check for corrupted rows first
    corrupted = check_for_corrupted_rows('service_hours.csv')
    if corrupted:
        print(f"Warning: Found {len(corrupted)} corrupted row(s). They will be skipped.")
    
    # Read service_hours.csv and aggregate hours per student
    try:
        if os.path.exists('service_hours.csv'):
            with open('service_hours.csv', 'r', newline='') as file:
                reader = csv.reader(file)
                for row_number, row in enumerate(reader, start=1):
                    # Skip corrupted rows
                    is_corrupted, _ = is_row_corrupted(row, row_number)
                    if is_corrupted:
                        continue
                    
                    if len(row) >= 4:
                        name = row[0].strip()
                        hours = float(row[2])
                        status = row[3].strip().lower()
                        
                        # Only count approved hours
                        if status == 'true':
                            if name not in student_hours:
                                student_hours[name] = 0.0
                            student_hours[name] += hours
    except FileNotFoundError:
        print("service_hours.csv not found. Creating empty total_hours.csv.")
    except Exception as e:
        print(f"Error reading service_hours.csv: {e}")
        return
    
    # Write aggregated hours to total_hours.csv (no duplicates)
    try:
        with open('total_hours.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Student Name', 'Total Hours'])  # Header
            for name in sorted(student_hours.keys()):  # Sort for consistency
                writer.writerow([name, student_hours[name]])
    except Exception as e:
        print(f"Error writing total_hours.csv: {e}")

try:
    user_name = input("Enter your name: ")
except ValueError:
    print("Invalid input. Please enter a valid number.")
    exit()

try:
    date = input("Enter the date (YYYY-MM-DD): ")
except ValueError:
    print("Invalid input. Please enter a valid date.")
    exit()

try:
    hours_worked = float(input("Enter number of service hours worked: "))
except ValueError:
    print("Invalid input. Please enter a valid number.")
    exit()

#validate user name is not empty
if not user_name:
    print("User name is required.")
    exit()

#validate hours > 0
if hours_worked <= 0:
    print("Hours worked must be greater than 0.")
    exit()

#validate date format
if not re.match(r'^\d{4}-\d{2}-\d{2}$', date):
    print("Invalid date format. Please use YYYY-MM-DD.")
    exit()

try:
    with open('service_hours.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([user_name, date, hours_worked, "false"])
except FileNotFoundError:
    print("File not found. Please check the file path.")
    exit()

# Update total hours CSV after adding new entry
create_total_hours_csv()
