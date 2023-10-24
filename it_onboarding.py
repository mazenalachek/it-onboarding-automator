"""
IT Onboarding Automator
A simple GUI application to automate IT user onboarding tasks.

This application collects new employee information and generates usernames
and passwords automatically. It saves records to a CSV file and logs all
actions to an audit log file.

Author: IT Onboarding Team
Purpose: Educational project for learning Python GUI programming
"""

# Import required modules from Python standard library
# tkinter is used for creating the GUI window and widgets
import tkinter as tk
from tkinter import messagebox

# csv module is used for reading and writing CSV files
import csv

# logging module is used for creating audit logs
import logging

# datetime module is used for getting current timestamps
from datetime import datetime

# os module is used for file system operations
import os

# secrets module is used for generating secure random passwords
import secrets
import string


def setup_logging():
    """
    Configure logging to write to audit.log file.

    This function sets up a logger that will write all actions
    to a file called audit.log with timestamps and log levels.

    Returns:
        logger: A configured logger object ready to use
    """
    # Create a logger object with a specific name
    logger = logging.getLogger("onboarding_logger")

    # Set the logging level to INFO (captures all important events)
    logger.setLevel(logging.INFO)

    # Check if the logger already has handlers to avoid duplicates
    if logger.handlers:
        # Return existing logger if it's already configured
        return logger

    # Create a file handler that writes to audit.log
    # mode='a' means append to existing file
    file_handler = logging.FileHandler("audit.log", mode="a")

    # Set the format for log messages
    # Format: timestamp - log level - message
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Apply the formatter to the file handler
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    # Return the configured logger
    return logger


def get_current_timestamp():
    """
    Get the current date and time formatted as a string.

    This function gets the current time and formats it
    in a consistent way for use in CSV files and reports.

    Returns:
        str: Current timestamp in format YYYY-MM-DD HH:MM:SS
    """
    # Get the current date and time
    now = datetime.now()

    # Format the datetime as a string
    # %Y = 4-digit year, %m = month, %d = day
    # %H = hour (24-hour), %M = minute, %S = second
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    # Return the formatted timestamp
    return timestamp


def file_exists(filepath):
    """
    Check if a file exists on the file system.

    This function checks if a specific file exists
    before trying to read from it.

    Args:
        filepath (str): The path to the file to check

    Returns:
        bool: True if file exists, False otherwise
    """
    # Use os.path.exists to check if the file exists
    exists = os.path.exists(filepath)

    # Return True or False
    return exists


def generate_username(email_prefix):
    """
    Generate a temporary username from the email prefix.

    This function takes an email prefix and adds 'temp_' to it
    to create a temporary username for new employees.

    Args:
        email_prefix (str): The prefix part of an email address

    Returns:
        str: A username starting with 'temp_' followed by the prefix
    """
    # Add the 'temp_' prefix to the email prefix
    username = "temp_" + email_prefix

    # Return the generated username
    return username


def generate_password():
    """
    Generate a secure random password.

    This function creates a 12-character password using
    letters, digits, and special characters.
    Uses the secrets module for better security than random.

    NOTE: This is for educational purposes and not suitable
    for production password generation.

    Returns:
        str: A 12-character random password
    """
    # Define the characters to use in the password
    # string.ascii_letters gives both uppercase and lowercase
    letters = string.ascii_letters

    # string.digits gives 0-9
    digits = string.digits

    # Create a string of special characters
    special = "!@#$%^&*"

    # Combine all character sets
    all_characters = letters + digits + special

    # Generate a 12-character password using secrets.choice
    # secrets is more secure than random for passwords
    password = ""

    # Loop 12 times to create 12 characters
    for i in range(12):
        # Choose one random character from all_characters
        char = secrets.choice(all_characters)

        # Add the character to the password string
        password = password + char

    # Return the generated password
    return password


def sanitize_csv_field(value):
    """
    Sanitize a value for safe storage in CSV format.

    This function checks if a value contains special characters
    that could break CSV format and wraps it in quotes if needed.

    Args:
        value (str): The value to sanitize

    Returns:
        str: The sanitized value safe for CSV storage
    """
    # Check if the value is empty
    if value == "":
        # Return empty string as is
        return ""

    # Check if the value contains any CSV-special characters
    # These are: comma, quote, or newline
    has_comma = "," in value
    has_quote = '"' in value
    has_newline = "\n" in value

    # If any special character is found, wrap in quotes
    if has_comma or has_quote or has_newline:
        # Wrap the value in double quotes
        sanitized = '"' + value + '"'

        # Return the sanitized value
        return sanitized
    else:
        # No special characters, return as is
        return value


def validate_fields(name, department, email_prefix, role):
    """
    Validate all input fields before processing.

    This function checks that all required fields are filled
    and meet minimum requirements. Returns a tuple with
    validation result and error message if invalid.

    Args:
        name (str): The employee's full name
        department (str): The department name
        email_prefix (str): The email prefix (username part)
        role (str): The employee's job role

    Returns:
        tuple: (is_valid, error_message)
            is_valid (bool): True if all fields are valid
            error_message (str): Error message if invalid, empty if valid
    """
    # Check if name field is empty
    if name == "" or name.isspace() or name is None:
        # Return invalid with error message
        return False, "Name cannot be empty"

    # Check if department field is empty
    if department == "" or department.isspace() or department is None:
        # Return invalid with error message
        return False, "Department cannot be empty"

    # Check if email prefix field is empty
    if email_prefix == "" or email_prefix.isspace() or email_prefix is None:
        # Return invalid with error message
        return False, "Email prefix cannot be empty"

    # Check if email prefix contains spaces (invalid format)
    if " " in email_prefix:
        # Return invalid with error message
        return False, "Email prefix cannot contain spaces"

    # Check if role field is empty
    if role == "" or role.isspace() or role is None:
        # Return invalid with error message
        return False, "Role cannot be empty"

    # Check minimum length for name (at least 2 characters)
    if len(name) < 2:
        # Return invalid with error message
        return False, "Name must be at least 2 characters"

    # Check minimum length for email prefix (at least 2 characters)
    if len(email_prefix) < 2:
        # Return invalid with error message
        return False, "Email prefix must be at least 2 characters"

    # All validations passed
    return True, ""


def save_to_csv(name, department, email_prefix, role, username, password):
    """
    Save employee data to the CSV file.

    This function saves a new employee record to onboarding_records.csv.
    It creates the file with a header if it doesn't exist.
    Handles various error conditions gracefully.

    Args:
        name (str): Employee's full name
        department (str): Department name
        email_prefix (str): Email prefix
        role (str): Job role
        username (str): Generated username
        password (str): Generated password

    Returns:
        tuple: (success, error_message)
            success (bool): True if save was successful
            error_message (str): Error message if failed, empty if successful
    """
    # Define the CSV filename
    csv_filename = "onboarding_records.csv"

    # Try to save the data to CSV
    try:
        # Sanitize all fields for CSV storage
        safe_name = sanitize_csv_field(name)
        safe_department = sanitize_csv_field(department)
        safe_email_prefix = sanitize_csv_field(email_prefix)
        safe_role = sanitize_csv_field(role)
        safe_username = sanitize_csv_field(username)
        safe_password = sanitize_csv_field(password)

        # Get current timestamp for the record
        timestamp = get_current_timestamp()

        # Check if the CSV file already exists
        file_is_new = not file_exists(csv_filename)

        # Open the CSV file in append mode
        # newline='' is required for csv module on Windows
        with open(csv_filename, mode="a", newline="", encoding="utf-8") as file:
            # Create a CSV writer object
            writer = csv.writer(file)

            # Check if this is a new file that needs a header
            if file_is_new:
                # Write the header row
                header = ["Name", "Department", "EmailPrefix", "Role",
                         "Username", "Password", "Timestamp"]
                writer.writerow(header)

            # Write the data row
            row = [safe_name, safe_department, safe_email_prefix,
                  safe_role, safe_username, safe_password, timestamp]
            writer.writerow(row)

        # Return success with no error message
        return True, ""

    # Handle permission errors (cannot write to file)
    except PermissionError:
        # Return failure with error message
        return False, "Permission denied: Cannot write to file"

    # Handle other OS errors (disk full, path too long, etc.)
    except OSError as e:
        # Return failure with error message
        return False, f"System error: {str(e)}"

    # Handle any other unexpected errors
    except Exception as e:
        # Return failure with error message
        return False, f"Unexpected error: {str(e)}"


def log_action(logger, action, status, details):
    """
    Log an action to the audit log file.

    This function writes a log entry with action type, status,
    and additional details to the audit.log file.

    Args:
        logger: The logger object from setup_logging()
        action (str): The action being performed (e.g., "GENERATE", "EXPORT")
        status (str): The status of the action (SUCCESS or ERROR)
        details (str): Additional details about the action

    Returns:
        bool: True if logging was successful, False otherwise
    """
    # Try to write the log entry
    try:
        # Create the log message string
        message = f"Action: {action} | Status: {status} | Details: {details}"

        # Write the message to the log
        logger.info(message)

        # Return success
        return True

    # Handle any logging errors
    except Exception:
        # Return failure
        return False


def show_status_message(status_var, root, message, duration=5000):
    """
    Display a status message in the status label.

    This function updates the status label with a message
    and schedules it to be cleared after a duration.

    Args:
        status_var: The StringVar connected to the status label
        root: The main tkinter window object
        message (str): The message to display
        duration (int): Time to show message in milliseconds (default 5000 = 5 seconds)
    """
    # Update the status variable with the message
    status_var.set(message)

    # Define a function to clear the status
    def clear_status():
        # Set the status variable to empty string
        status_var.set("")

    # Schedule the clear_status function to run after duration milliseconds
    root.after(duration, clear_status)


def clear_input_fields(entries):
    """
    Clear all input fields in the GUI.

    This function resets all entry fields to empty strings
    after a successful record generation.

    Args:
        entries (dict): Dictionary of entry widgets

    Returns:
        bool: True if all fields were cleared successfully
    """
    # Try to clear all fields
    try:
        # Loop through each entry in the entries dictionary
        for field_name in entries:
            # Get the entry widget for this field
            entry_widget = entries[field_name]

            # Set the entry value to empty string
            entry_widget.delete(0, tk.END)

        # Return success
        return True

    # Handle any errors
    except Exception:
        # Return failure
        return False


def create_gui():
    """
    Create and configure the main GUI window.

    This function creates the main tkinter window with
    title and size settings.

    Returns:
        root: The main tkinter window object
    """
    # Create the main window
    root = tk.Tk()

    # Set the window title
    root.title("IT Onboarding Automator")

    # Set the window size (width x height)
    root.geometry("500x500")

    # Make the window non-resizable for simplicity
    root.resizable(False, False)

    # Return the window object
    return root


def create_input_fields(parent):
    """
    Create all input fields for the GUI.

    This function creates labels and entry widgets for
    all required input fields.

    Args:
        parent: The parent widget (usually the main window)

    Returns:
        dict: Dictionary containing the entry widgets
    """
    # Create a dictionary to store the entry widgets
    entries = {}

    # Create Full Name field
    # Create label for Full Name
    name_label = tk.Label(parent, text="Full Name:")
    # Add label to the window with padding
    name_label.pack(pady=(20, 5))
    # Create entry widget for Full Name
    name_entry = tk.Entry(parent, width=40)
    # Add entry to the window
    name_entry.pack(pady=5)
    # Store the entry in our dictionary
    entries["name"] = name_entry

    # Create Department field
    # Create label for Department
    dept_label = tk.Label(parent, text="Department:")
    # Add label to the window with padding
    dept_label.pack(pady=5)
    # Create entry widget for Department
    dept_entry = tk.Entry(parent, width=40)
    # Add entry to the window
    dept_entry.pack(pady=5)
    # Store the entry in our dictionary
    entries["department"] = dept_entry

    # Create Email Prefix field
    # Create label for Email Prefix
    email_label = tk.Label(parent, text="Email Prefix:")
    # Add label to the window with padding
    email_label.pack(pady=5)
    # Create entry widget for Email Prefix
    email_entry = tk.Entry(parent, width=40)
    # Add entry to the window
    email_entry.pack(pady=5)
    # Store the entry in our dictionary
    entries["email_prefix"] = email_entry

    # Create Role field
    # Create label for Role
    role_label = tk.Label(parent, text="Role:")
    # Add label to the window with padding
    role_label.pack(pady=5)
    # Create entry widget for Role
    role_entry = tk.Entry(parent, width=40)
    # Add entry to the window
    role_entry.pack(pady=5)
    # Store the entry in our dictionary
    entries["role"] = role_entry

    # Return the dictionary of entry widgets
    return entries


def create_status_label(parent):
    """
    Create the status label for displaying messages.

    This function creates a label that shows status messages
    to the user. Returns both the widget and the variable.

    Args:
        parent: The parent widget (usually the main window)

    Returns:
        tuple: (status_label_widget, status_variable)
    """
    # Create a StringVar to hold the status text
    status_var = tk.StringVar()

    # Set initial status message
    status_var.set("Ready")

    # Create the status label with the StringVar
    status_label = tk.Label(parent, textvariable=status_var,
                          fg="blue", font=("Arial", 10))

    # Add the label to the window with padding
    status_label.pack(pady=20)

    # Return both the widget and the variable
    return status_label, status_var


def create_buttons(parent, entries, status_var, logger, root):
    """
    Create the action buttons for the GUI.

    This function creates the Generate and Export Report buttons
    and connects them to their handler functions.

    Args:
        parent: The parent widget (usually the main window)
        entries: Dictionary of entry widgets
        status_var: StringVar for status updates
        logger: Logger object for audit logging
        root: Main window for scheduling functions

    Returns:
        None
    """
    # Create a frame to hold the buttons
    button_frame = tk.Frame(parent)

    # Add the frame to the window
    button_frame.pack(pady=10)

    # Create Generate button
    # Use lambda to pass arguments to the handler function
    generate_button = tk.Button(
        button_frame,
        text="Generate",
        command=lambda: on_generate(entries, status_var, logger, root),
        width=15,
        height=2,
        bg="green",
        fg="white"
    )

    # Add the Generate button to the frame
    generate_button.pack(side=tk.LEFT, padx=10)

    # Create Export Report button
    export_button = tk.Button(
        button_frame,
        text="Export Report",
        command=lambda: on_export_report(status_var, logger, root),
        width=15,
        height=2,
        bg="blue",
        fg="white"
    )

    # Add the Export button to the frame
    export_button.pack(side=tk.LEFT, padx=10)


def on_generate(entries, status_var, logger, root):
    """
    Handle the Generate button click event.

    This function is called when the user clicks the Generate button.
    It validates input, generates credentials, saves to CSV, and logs the action.

    Args:
        entries: Dictionary of entry widgets
        status_var: StringVar for status updates
        logger: Logger object for audit logging
        root: Main window for scheduling functions

    Returns:
        None
    """
    # Get values from all entry fields
    name = entries["name"].get()
    department = entries["department"].get()
    email_prefix = entries["email_prefix"].get()
    role = entries["role"].get()

    # Validate all input fields
    is_valid, error_message = validate_fields(name, department, email_prefix, role)

    # Check if validation failed
    if not is_valid:
        # Show error message in status label
        show_status_message(status_var, root, f"Error: {error_message}")

        # Log the validation error
        log_action(logger, "GENERATE", "ERROR", error_message)

        # Return without saving
        return

    # All fields are valid, proceed with generation

    # Generate username
    username = generate_username(email_prefix)

    # Generate password
    password = generate_password()

    # Try to save to CSV
    success, error = save_to_csv(name, department, email_prefix,
                                role, username, password)

    # Check if save was successful
    if success:
        # Create success message with credentials
        success_msg = f"Success! Username: {username}, Password: {password}"

        # Show success message in status label
        show_status_message(status_var, root, success_msg)

        # Log the successful action
        details = f"User: {name}, Dept: {department}, Role: {role}"
        log_action(logger, "GENERATE", "SUCCESS", details)

        # Clear the input fields for next entry
        clear_input_fields(entries)
    else:
        # Save failed, show error message
        show_status_message(status_var, root, f"Error: {error}")

        # Log the error
        log_action(logger, "GENERATE", "ERROR", error)


def on_export_report(status_var, logger, root):
    """
    Handle the Export Report button click event.

    This function is called when the user clicks Export Report.
    It reads the CSV file and creates a markdown report.

    Args:
        status_var: StringVar for status updates
        logger: Logger object for audit logging
        root: Main window for scheduling functions

    Returns:
        None
    """
    # Define the CSV filename
    csv_filename = "onboarding_records.csv"

    # Check if the CSV file exists
    if not file_exists(csv_filename):
        # File doesn't exist, show error
        show_status_message(status_var, root,
                          "Error: No records found. Generate records first.")

        # Log the error
        log_action(logger, "EXPORT", "ERROR", "CSV file does not exist")

        # Return without exporting
        return

    # CSV file exists, try to read it
    try:
        # Open the CSV file for reading
        with open(csv_filename, mode="r", newline="", encoding="utf-8") as file:
            # Create a CSV reader object
            reader = csv.reader(file)

            # Read all rows from the CSV
            rows = list(reader)

        # Check if the CSV has any data (besides header)
        if len(rows) <= 1:
            # Only header row exists or file is empty
            show_status_message(status_var, root,
                              "Error: No records to export")

            # Log the error
            log_action(logger, "EXPORT", "ERROR", "No data records in CSV")

            # Return without exporting
            return

        # Start building the markdown report
        report = []

        # Add report title
        report.append("# IT Onboarding Report\n")

        # Add generation timestamp
        timestamp = get_current_timestamp()
        report.append(f"*Generated: {timestamp}*\n")

        # Add summary section header
        report.append("\n## Summary\n")

        # Count total users (subtract 1 for header row)
        total_users = len(rows) - 1
        report.append(f"- Total Users: {total_users}\n")

        # Collect unique departments
        departments = set()

        # Loop through all data rows (skip header)
        for row in rows[1:]:
            # Get department from column index 1
            if len(row) > 1:
                departments.add(row[1])

        # Add departments to summary
        report.append(f"- Departments: {', '.join(sorted(departments))}\n")

        # Add table section header
        report.append("\n## User Accounts\n")

        # Create markdown table header
        # Note: We exclude the Password column for security
        table_header = "| Name | Department | Email Prefix | Role | Username | Created |"
        report.append(table_header + "\n")

        # Add table separator
        table_separator = "|------|------------|--------------|------|----------|---------|"
        report.append(table_separator + "\n")

        # Loop through all data rows (skip header)
        for row in rows[1:]:
            # Make sure the row has data
            if len(row) >= 7:
                # Extract fields from the row
                # Index mapping: 0=Name, 1=Department, 2=EmailPrefix,
                #              3=Role, 4=Username, 5=Password (skip), 6=Timestamp
                name = row[0]
                department = row[1]
                email_prefix = row[2]
                role = row[3]
                username = row[4]
                created = row[6]

                # Create table row (excluding password)
                table_row = f"| {name} | {department} | {email_prefix} | {role} | {username} | {created} |"
                report.append(table_row + "\n")

        # Add footer to report
        report.append("\n---\n")
        report.append("*Note: Passwords are not included in this report for security.*\n")

        # Join all report lines into a single string
        report_content = "".join(report)

        # Write the report to a markdown file
        report_filename = "onboarding_report.md"
        with open(report_filename, mode="w", encoding="utf-8") as file:
            # Write the report content
            file.write(report_content)

        # Show success message
        show_status_message(status_var, root,
                          f"Report exported to {report_filename}")

        # Log the successful export
        log_action(logger, "EXPORT", "SUCCESS",
                  f"Report created with {total_users} users")

    # Handle file not found (deleted between check and read)
    except FileNotFoundError:
        # Show error message
        show_status_message(status_var, root, "Error: File not found")

        # Log the error
        log_action(logger, "EXPORT", "ERROR", "File not found during read")

    # Handle permission errors
    except PermissionError:
        # Show error message
        show_status_message(status_var, root,
                          "Error: Permission denied reading file")

        # Log the error
        log_action(logger, "EXPORT", "ERROR", "Permission denied")

    # Handle CSV parsing errors
    except csv.Error:
        # Show error message
        show_status_message(status_var, root,
                          "Error: Invalid CSV format")

        # Log the error
        log_action(logger, "EXPORT", "ERROR", "CSV parsing error")

    # Handle any other unexpected errors
    except Exception as e:
        # Show error message
        show_status_message(status_var, root,
                          f"Error: {str(e)}")

        # Log the error
        log_action(logger, "EXPORT", "ERROR", f"Unexpected error: {str(e)}")


def main():
    """
    Main function to start the application.

    This function sets up logging, creates the GUI,
    and starts the main event loop.
    """
    # Set up the logging system
    logger = setup_logging()

    # Create the main GUI window
    root = create_gui()

    # Create input fields
    entries = create_input_fields(root)

    # Create status label
    status_label, status_var = create_status_label(root)

    # Create action buttons
    create_buttons(root, entries, status_var, logger, root)

    # Start the tkinter main event loop
    # This keeps the window open and responsive
    root.mainloop()


# This code runs when the script is executed directly
if __name__ == "__main__":
    # Call the main function to start the application
    main()
