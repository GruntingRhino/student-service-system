import csv
import re

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

with open('service_hours.csv', mode='a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([user_name, date, hours_worked, "false"])