import re
import os
import streamlit as st

# -------------------------------------------------------------
# NC file modifier utility
# -------------------------------------------------------------

def modify_nc_file(input_nc_path: str) -> str:
    """Read an .NC file, perform a series of edits, and return the path
    of the modified file.

    Edits performed
    --------------
    1. Change the top‑of‑file O‑number to match the file name.
    2. Replace the last H0 call with H[last M6 T#] and set Z to 15.
    3. Adjust the following XY move to X‑11 / Y9.
    4. Remove all other H0 lines.
    5. After *every* M6 line, insert a new T‑line that calls the tool
       number from the *next* M6 below.  For the final M6 (where there is
       no "next" M6), wrap around and use the tool number from the *first*
       M6 in the file.
    """

    # ---------------------------------------------------------
    # Prep / load
    # ---------------------------------------------------------
    file_stem = os.path.splitext(os.path.basename(input_nc_path))[0]
    out_ext = os.path.splitext(input_nc_path)[1].replace(".NC", ".txt")

    with open(input_nc_path, "r") as fh:
        lines = fh.readlines()

    # ---------------------------------------------------------
    # 1.  Top‑of‑file O‑number
    # ---------------------------------------------------------
    if lines and lines[0].startswith("%") and len(lines) > 1 and lines[1].startswith("N100 O"):
        lines[1] = re.sub(r"O\d+", f"O{file_stem}", lines[1])

    # ---------------------------------------------------------
    # 2a.  Last M6 tool number
    # ---------------------------------------------------------
    last_tool_num = None
    for i in range(len(lines) - 1, -1, -1):
        if "M6" in lines[i]:
            m = re.search(r"T(\d+)", lines[i])
            if m:
                last_tool_num = int(m.group(1))
            break

    # ---------------------------------------------------------
    # 2b.  Swap last H0, set Z15
    # ---------------------------------------------------------
    last_h0_idx = None
    if last_tool_num is not None:
        for i in range(len(lines) - 1, -1, -1):
            if "H0" in lines[i]:
                lines[i] = re.sub(r"H0", f"H{last_tool_num}", lines[i])
                lines[i] = re.sub(r"Z[\d.-]+", "Z15.", lines[i])
                last_h0_idx = i
                break

    # ---------------------------------------------------------
    # 2c.  Adjust XY move immediately after last H0
    # ---------------------------------------------------------
    if last_h0_idx is not None and last_h0_idx + 1 < len(lines):
        lines[last_h0_idx + 1] = re.sub(r"X[\d.-]+", "X-11.", lines[last_h0_idx + 1])
        lines[last_h0_idx + 1] = re.sub(r"Y[\d.-]+", "Y9.", lines[last_h0_idx + 1])

    # ---------------------------------------------------------
    # Remove all other H0 lines
    # ---------------------------------------------------------
    lines = [ln for idx, ln in enumerate(lines) if "H0" not in ln or idx == last_h0_idx]

    # ---------------------------------------------------------
    # 3.  Insert follow‑up T‑lines after every M6 (with wrap‑around)
    # ---------------------------------------------------------
    new_lines: list[str] = []
    first_tool_num: str | None = None

    for i, ln in enumerate(lines):
        new_lines.append(ln)

        if "M6" in ln:
            # Capture tool number on *this* M6 line
            m_curr = re.search(r"T(\d+)", ln)
            if not m_curr:
                continue
            curr_tool = m_curr.group(1)
            if first_tool_num is None:
                first_tool_num = curr_tool  # remember for wrap‑around

            # Look ahead for the next M6 to get its tool number
            next_tool: str | None = None
            for j in range(i + 1, len(lines)):
                if "M6" in lines[j]:
                    m_next = re.search(r"T(\d+)", lines[j])
                    if m_next:
                        next_tool = m_next.group(1)
                    break

            tool_to_write = next_tool or first_tool_num  # wrap if needed
            if tool_to_write:
                # Derive a new line number: current N‑number + 5 (fallback 0)
                try:
                    curr_n = int(re.match(r"N(\d+)", ln).group(1))
                except (AttributeError, ValueError):
                    curr_n = 0
                new_lines.append(f"N{curr_n + 5} T{tool_to_write}\n")

    # ---------------------------------------------------------
    # Write result (with conflict‑safe rename)
    # ---------------------------------------------------------
    temp_out = os.path.join(os.path.dirname(input_nc_path), f"{file_stem} Original{out_ext}")
    with open(temp_out, "w") as fh:
        fh.writelines(new_lines)

    final_out = temp_out.replace(" Original", " Roshed")
    if os.path.exists(final_out):
        base, ext = os.path.splitext(final_out)
        idx = 1
        while os.path.exists(f"{base}_{idx}{ext}"):
            idx += 1
        final_out = f"{base}_{idx}{ext}"

    os.rename(temp_out, final_out)
    return final_out


# -------------------------------------------------------------
# Streamlit front‑end
# -------------------------------------------------------------

st.title("NC File Modifier")

uploaded_file = st.file_uploader("Upload your .NC file", type=["NC"])

if uploaded_file:
    with st.spinner("Processing file..."):
        os.makedirs("uploads", exist_ok=True)
        input_path = os.path.join("uploads", uploaded_file.name)
        with open(input_path, "wb") as fh:
            fh.write(uploaded_file.getbuffer())

        modified_path = modify_nc_file(input_path)

    st.success("File has been modified successfully!")
    with open(modified_path, "rb") as fh:
        st.download_button(
            label="Download Modified File",
            data=fh,
            file_name=os.path.basename(modified_path),
            mime="text/plain",
        )