import streamlit as st
def modify_nc_file(input_nc_path):
    import re
    import os

    # Extract the filename without extension to use as the "O" number
    file_name = os.path.splitext(os.path.basename(input_nc_path))[0]
    file_type = os.path.splitext(os.path.basename(input_nc_path))[1]
    
    tool_numbers = set()  # Use a set to store unique tool numbers

    with open(input_nc_path, 'r') as file:
        lines = file.readlines()

    # Step 1: Modify the "O" number at the top
    if lines[0].startswith('%') and lines[1].startswith('N100 O'):
        lines[1] = re.sub(r'O\d+', f'O{file_name}', lines[1])  # Replace O number with the file name

    # Step 2a: Find the line with the last "M6" and extract the tool number
    file_name = file_name + " Original"
    last_m6_tool_number = None
    for i in range(len(lines) - 1, -1, -1):  # Iterate backward through the lines
        if "M6" in lines[i]:
            match = re.search(r'T(\d+)', lines[i])  # Extract the tool number (e.g., T3)
            if match:
                tool_number = int(match.group(1))
                tool_numbers.add(tool_number)  # Add to the set of tool numbers
                last_m6_tool_number = tool_number
            break

    # Step 2b: Replace the last "H0" with H[last_tool_number] and update Z value
    last_h0_index = None
    if last_m6_tool_number:  # Only proceed if a tool number was found
        for i in range(len(lines) - 1, -1, -1):  # Iterate backward to find the last "H0"
            if "H0" in lines[i]:
                lines[i] = re.sub(r'H0', f'H{last_m6_tool_number}', lines[i])  # Replace H0 with H[last_tool_number]
                lines[i] = re.sub(r'Z[\d.-]+', 'Z15.', lines[i])  # Replace Z value with Z15
                last_h0_index = i
                break

    # Step 2c: Modify the next line's X and Y values
    if last_h0_index is not None and last_h0_index + 1 < len(lines):
        lines[last_h0_index + 1] = re.sub(r'X[\d.-]+', 'X-11.', lines[last_h0_index + 1])  # Update X to -14.5
        lines[last_h0_index + 1] = re.sub(r'Y[\d.-]+', 'Y9.', lines[last_h0_index + 1])  # Update Y to 12.

    # Step 3b: Ensure all M6 callouts are followed by the correct H offset
    for j in range(len(lines)):
        if "M6" in lines[j]:
            match = re.search(r'T(\d+)', lines[j])  # Look for T#
            if match:
                tool_number = int(match.group(1))  # Extract the tool number as an integer
                tool_numbers.add(tool_number)  # Add to the set of tool numbers
                if tool_number == last_m6_tool_number:
                    continue
                if tool_number == 1:
                    tool_number_minus_one = last_m6_tool_number
                else:
                    tool_number_minus_one = tool_number - 1
                if j + 1 < len(lines) and f'H{tool_number}' not in lines[j + 1]:
                    lines.insert(j + 1, f'N{int(lines[j].split()[0][1:]) + 5} T{tool_number_minus_one}\n')

    print("All M6 callouts are followed by an H")
    print("Your file has been Roshed YAY!")

    # Sort and print the tool numbers
    tool_numbers = sorted(tool_numbers)  # Sort tool numbers
    print("Tool Numbers Found:", tool_numbers)

    output_file_path = os.path.join(os.path.dirname(input_nc_path), f"{file_name}{file_type}")
    if os.path.exists(output_file_path):
        base, ext = os.path.splitext(output_file_path)
        counter = 1
        while os.path.exists(f"{base}_{counter}{ext}"):
            counter += 1
        output_file_path = f"{base}_{counter}{ext}"

    with open(output_file_path, "w") as output_file:
        output_file.writelines(lines)

    final_output_path = output_file_path.replace(" Original", " Roshed")
    if os.path.exists(final_output_path):
        base, ext = os.path.splitext(final_output_path)
        counter = 1
        while os.path.exists(f"{base}_{counter}{ext}"):
            counter += 1
        final_output_path = f"{base}_{counter}{ext}"

    os.rename(output_file_path, final_output_path)
    return tool_numbers, final_output_path
