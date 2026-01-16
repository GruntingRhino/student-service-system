import csv
import os
import re

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
    """
    Creates or updates a total_hours.csv file with aggregated hours per student.
    Ensures no duplicate entries per student.
    Only counts approved hours (status == 'true').
    """
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

def get_student_total_hours(student_name):
    """
    Reads total_hours.csv and returns the total hours for a specific student.
    
    Args:
        student_name (str): Name of the student to look up
    
    Returns:
        float: Total hours for the student, or 0.0 if student not found
    """
    try:
        if not os.path.exists('total_hours.csv'):
            print("total_hours.csv not found. Creating it now...")
            create_total_hours_csv()
        
        with open('total_hours.csv', 'r', newline='') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row_number, row in enumerate(reader, start=2):  # Start at 2 (after header)
                if len(row) >= 2:
                    name = row[0].strip()
                    try:
                        hours = float(row[1])
                        if name.lower() == student_name.lower():
                            return hours
                    except (ValueError, IndexError):
                        print(f"Warning: Skipping corrupted row {row_number} in total_hours.csv: {row}")
                        continue
        return 0.0  # Student not found
    except FileNotFoundError:
        print("total_hours.csv not found.")
        return 0.0
    except Exception as e:
        print(f"Error reading total_hours.csv: {e}")
        return 0.0

students = {}

class Student:
    def __init__(self, name):
        self.name = name
        self.total_hours = 0.0

    def add_hours(self, hours):
        self.total_hours += hours

# Check for corrupted rows before processing
corrupted = check_for_corrupted_rows('service_hours.csv')
if corrupted:
    print(f"Warning: Found {len(corrupted)} corrupted row(s). They will be skipped.")

try:
    with open('service_hours.csv', 'r', newline='') as file:
        reader = csv.reader(file)
        for row_number, row in enumerate(reader, start=1):
            # Skip corrupted rows
            is_corrupted, _ = is_row_corrupted(row, row_number)
            if is_corrupted:
                continue
            
            if len(row) >= 4:
                name = row[0].strip()
                try:
                    hours = float(row[2])
                    
                    if name not in students:
                        students[name] = Student(name)
                    
                    students[name].add_hours(hours)
                except (ValueError, IndexError) as e:
                    print(f"Skipping row {row_number}: Error processing hours - {e}")
                    continue
except FileNotFoundError:
    print("File not found. Please check the file path.")
    exit()

# Print totals
for student in students.values():
    print(student.name, student.total_hours)

# Also read from total_hours.csv and report
print("\n=== Total Hours from total_hours.csv ===")
for student in students.values():
    total_hours = get_student_total_hours(student.name)
    print(f"{student.name}: {total_hours} hours")
