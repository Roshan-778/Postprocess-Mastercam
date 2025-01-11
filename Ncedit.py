import re
import os

# gets and checks Input path exist's 
input_nc_path = input("Please give me your input file path: ").strip('"')  # Replace with your input file path
if os.path.exists(input_nc_path):
    if os.path.isfile(input_nc_path):
        print(f"The file '{input_nc_path}' exists. Finalizing now...")

def modify_nc_file(input_nc_path): 
    # Extract the filename without extension to use as the "O" number
    file_name = os.path.splitext(os.path.basename(input_nc_path))[0]
    file_type = os.path.splitext(os.path.basename(input_nc_path))[1]
    file_type = file_type.replace(".NC", ".txt")
    print(f"Input file has been renamed {file_name}{file_type}")
    
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
                last_m6_tool_number = int(match.group(1))
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
        lines[last_h0_index + 1] = re.sub(r'X[\d.-]+', 'X-11', lines[last_h0_index + 1])  # Update X to -14.5
        lines[last_h0_index + 1] = re.sub(r'Y[\d.-]+', 'Y9.', lines[last_h0_index + 1])  # Update Y to 12.

    # Step 3a: Delete all other lines containing H0 (after handling Step 2a)
    lines = [line for idx, line in enumerate(lines) if 'H0' not in line or idx == last_h0_index]

    # Step 3b: Ensure all M6 callouts are followed by the correct H offset
    for j in range(len(lines)):
        if "M6" in lines[j]:
            # Find the tool number in the M6 line (e.g., T3 M6)
            match = re.search(r'T(\d+)', lines[j])  # Look for T#
            if match:
                tool_number = int(match.group(1))  # Extract the tool number as an integer

                # Skip processing if the tool number matches the last "M6" tool number
                if tool_number == last_m6_tool_number:
                    continue

                # Check if the tool number is 1, and if so, set it to 5
                if tool_number == 1:
                    tool_number_minus_one = 5
                else:
                    tool_number_minus_one = tool_number - 1  # Subtract 1 from the tool number

                # Check if the next line already contains the correct H offset
                if j + 1 < len(lines) and f'H{tool_number}' not in lines[j + 1]:
                    # Add a new line with T[tool_number_minus_one]
                    lines.insert(j + 1, f'N{int(lines[j].split()[0][1:]) + 5} T{tool_number_minus_one}\n')

    
    output_file_path = os.path.join(os.path.dirname(input_nc_path), f"{file_name}{file_type}")
    with open(output_file_path, "w") as output_file:
        output_file.writelines(lines)
    print(f"Modified file saved to: {output_file_path}")
    #renameing the modified file
    output_file_path = output_file_path.replace(" Original", " Roshed")
    print(f"{output_file_path}")
    html_link = f'<a href="file:///{output_file_path}" target="_blank">Click here to open the file</a>'
    print(html_link)

# Call the function
modify_nc_file(input_nc_path)

