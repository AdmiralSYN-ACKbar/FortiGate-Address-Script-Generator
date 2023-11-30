import csv
import ipaddress
import time
import tkinter as tk
from tkinter import filedialog, ttk
import os

def generate_script(input_csv, output_path, output_box):
    try:
        with open(input_csv, 'r') as file:
            reader = csv.DictReader(file)
            groups = {}
            group_comments = {}
            count = 0

            # Remove the existing extension and replace it with .txt
            output_path = os.path.splitext(output_path)[0] + '.txt'

            with open(output_path, 'w') as output_file:
                for row in reader:
                    name = row['name']
                    value = row['value']
                    group = row['group']
                    comments = row.get('comments', '')  # Get the comments field, default to empty string if not present
                    group_comment = row.get('group_comments', '')  # Get the group comment field, default to empty string if not present

                    # Split the value into IP and subnet mask
                    if '/' in value:
                        ip, mask = value.split('/')
                        object_type = "subnet"
                    else:
                        ip = value
                        mask = '32'  # Default to /32 if no mask is provided
                        try:
                            ipaddress.ip_address(ip)
                            object_type = "subnet"
                        except ValueError:
                            object_type = "fqdn"

                    if object_type == "subnet":
                        output_file.write(f"config firewall address\nedit {name}\nset type ipmask\nset subnet {ip}/{mask}\nset comment \"{comments}\"\nnext\nend\n")
                    else:
                        output_file.write(f"config firewall address\nedit {name}\nset type {object_type}\nset fqdn {ip}\nset comment \"{comments}\"\nnext\nend\n")

                    if group:
                        if group not in groups:
                            groups[group] = []
                        if group_comment:  # Only set the comment if group_comment is not empty
                            group_comments[group] = group_comment
                        groups[group].append(name)

                    count += 1

                for group, members in groups.items():
                    output_file.write(f"config firewall addrgrp\nedit {group}\n")
                    if group in group_comments:  # Only write the comment if it's in group_comments
                        output_file.write(f"set comment \"{group_comments[group]}\"\n")
                    for member in members:
                        output_file.write(f"append member {member}\n")
                    output_file.write("next\nend\n")

            output_box.delete('1.0', tk.END)  # Clear the status box
            output_box.insert(tk.END, f"{time.strftime('%Y-%m-%d %H:%M:%S')}: Successfully wrote {count} objects to {output_path}\n")
    except Exception as e:
        output_box.delete('1.0', tk.END)  # Clear the status box
        output_box.insert(tk.END, f"{time.strftime('%Y-%m-%d %H:%M:%S')}: Error: {str(e)}\n")
def browse_file(entry):
    filename = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
    entry.delete(0, tk.END)
    entry.insert(0, filename)

def browse_output_file(entry):
    filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    entry.delete(0, tk.END)
    entry.insert(0, filename)

def main():
    root = tk.Tk()
    root.title("Admiral SYN-ACKbar's FortiGate Address Script Generator")  # Change the title here
    root.geometry("500x500")

    frame = ttk.Frame(root, padding="10 10 10 10")
    frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    title_label1 = ttk.Label(frame, text="Admiral SYN-ACKbar's", font=("Sylfaen", 14, "italic"))
    title_label1.grid(row=0, column=0, columnspan=3)
    title_label2 = ttk.Label(frame, text="FortiGate Address Script Generator", font=("Sylfaen", 18, "bold"))
    title_label2.grid(row=1, column=0, columnspan=3)

    input_csv_label = ttk.Label(frame, text="Input CSV:", font=("Sylfaen", 10, "bold"))
    input_csv_label.grid(row=2, column=0, sticky=tk.W)
    input_csv_entry = ttk.Entry(frame, width=30)
    input_csv_entry.grid(row=2, column=1, sticky=(tk.W, tk.E))
    input_csv_button = ttk.Button(frame, text="Browse", command=lambda: browse_file(input_csv_entry))
    input_csv_button.grid(row=2, column=2, sticky=tk.W)

    output_file_label = ttk.Label(frame, text="Output File:", font=("Sylfaen", 10, "bold"))
    output_file_label.grid(row=3, column=0, sticky=tk.W)
    output_file_entry = ttk.Entry(frame, width=30)
    output_file_entry.grid(row=3, column=1, sticky=(tk.W, tk.E))
    output_file_button = ttk.Button(frame, text="Browse", command=lambda: browse_output_file(output_file_entry))
    output_file_button.grid(row=3, column=2, sticky=tk.W)

    generate_button = tk.Button(frame, text="ENGAGE", command=lambda: generate_script(input_csv_entry.get(), output_file_entry.get(), output_box), width=20, font=("Sylfaen", 14, "bold"), foreground="blue")
    generate_button.grid(row=4, column=0, columnspan=3)

    output_label = ttk.Label(frame, text="Status:", font=("Sylfaen", 14, "bold"))
    output_label.grid(row=5, column=0, sticky=tk.W)
    output_box = tk.Text(frame, width=50, height=10)  
    output_box.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E))
       
    for child in frame.winfo_children(): 
        child.grid_configure(padx=5, pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()