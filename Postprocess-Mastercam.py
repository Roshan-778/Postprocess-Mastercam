import re
import os
import streamlit as st

# Function to modify the NC file
def modify_nc_file(input_nc_path):
    # Extract the filename without extension to use as the "O" number
    file_name = os.path.splitext(os.path.basename(input_nc_path))[0]
    file_type = os.path.splitext(os.path.basename(input_nc_path))[1]
    file_type = file_type.replace(".NC", ".txt")

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
        lines[last_h0_index + 1] = re.sub(r'X[\d.-]+', 'X-11.', lines[last_h0_index + 1])  # Update X to -11
        lines[last_h0_index + 1] = re.sub(r'Y[\d.-]+', 'Y9.', lines[last_h0_index + 1])  # Update Y to 9

    # Remove all "H0" lines except the last one
    lines = [line for idx, line in enumerate(lines) if 'H0' not in line or idx == last_h0_index]
    if not any('H0' in line for line in lines):
        print("The new file has no H0's")

    # Step 3: Ensure all M6 callouts are followed by a new line with the T# from the next M6 line below
    new_lines = []  # To store the modified lines
    for i in range(len(lines)):
        new_lines.append(lines[i])  # Add the current line to the new lines list

        if "M6" in lines[i]:  # Check if the current line contains M6
            match_current = re.search(r'T(\d+)', lines[i])  # Extract the current T#
            if match_current:  # Ensure we have a tool number in the current line
                # Look for the next M6 line below and extract its T#
                for j in range(i + 1, len(lines)):  # Search subsequent lines
                    if "M6" in lines[j]:  # Find the next M6
                        match_below = re.search(r'T(\d+)', lines[j])  # Extract T# from the line below
                        if match_below:
                            tool_number_below = match_below.group(1)  # Get the tool number below
                            # Generate the new line with the tool number below
                            line_number = int(lines[i].split()[0][1:]) + 5  # Increment line number by 5
                            new_lines.append(f'N{line_number} T{tool_number_below}\n')  # Add the new line
                        break  # Stop searching after finding the next M6

    # Write the modified file
    output_file_path = os.path.join(os.path.dirname(input_nc_path), f"{file_name}{file_type}")
    with open(output_file_path, "w") as output_file:
        output_file.writelines(new_lines)

    # Handle conflicts for renaming final_output_path
    final_output_path = output_file_path.replace(" Original", " Roshed")
    if os.path.exists(final_output_path):
        base, ext = os.path.splitext(final_output_path)
        counter = 1
        while os.path.exists(f"{base}_{counter}{ext}"):
            counter += 1
        final_output_path = f"{base}_{counter}{ext}"

    os.rename(output_file_path, final_output_path)
    return final_output_path

# Streamlit app
st.title("NC File Modifier")

uploaded_file = st.file_uploader("Upload your .NC file", type=["NC"])

if uploaded_file:
    with st.spinner("Processing file..."):
        input_path = os.path.join("uploads", uploaded_file.name)
        os.makedirs("uploads", exist_ok=True)
        with open(input_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        modified_file_path = modify_nc_file(input_path)
        st.success("File has been modified successfully!")

        # Provide a download link
        with open(modified_file_path, "rb") as modified_file:
            st.download_button(
                label="Download Modified File",
                data=modified_file,
                file_name=os.path.basename(modified_file_path),
                mime="text/plain"
            )
