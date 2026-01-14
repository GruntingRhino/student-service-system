import csv

user_name = input("Enter your name: ")
date = input("Enter the date (YYYY-MM-DD): ")
hours_worked = float(input("Enter number of service hours worked: "))

with open('service_hours.csv', mode='a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([user_name, date, hours_worked])