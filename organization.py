import csv

rows = []

# Step 1: Read entire CSV into memory
with open('service_hours.csv', 'r', newline='') as file:
    reader = csv.reader(file)
    rows = list(reader)

# Step 2: Modify rows
for row in rows:
    if row[3].lower() == "false":
        status = input(f"{row[0]}'s hours are pending approval. Approve? (y/n): ")
        if status.lower() == "y":
            row[3] = "true"
            print(f"{row[0]}'s hours have been approved.")
        else:
            print(f"{row[0]}'s hours remain unapproved.")

# Step 3: Write everything back
with open('service_hours.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(rows)
