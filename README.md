# Postprocess-Mastercam link: https://postprocess-mastercam.streamlit.app/
# This app helps with pragramming a CNC Machine by post processing Your G-code by macking more edits to the file, so you are able to run the code on the machines at OSU.
# This app will do seven things.
# 1. Change the "O" number at the top of the program to a 4-digit number other than "0000."
# 2. Update the last occurrence of "H0" to "H[last tool number]."
# 3. In the same line, change the Z value to "15."
# 4. In the next line, change the X and Y values from (0,0) to (-14.5,12).
# 5. Delete all other lines containing "H0" (except the one updated in step 2).
# 6. Verify all "M6" callouts are followed by the correct tool length offsets:
#    Example: T1 M6 → H1
#    Example: T5 M6 → H5.
# 7. For every "M6" call:
#    Locate the next "M6" call and identify the associated tool.
#    Add a new line after the original "M6" call that includes the tool associated with the next "M6" call (e.g., if the next tool is T5, insert a line referencing T5).
# After you have used a pragram like Mastercam to create a visualy of all your tools paths and run what you have and run thr visual through the post processor givin to you by MaterCam, you can use my app
# Before you open my app please make sure the the file is a .NC file and that the name of the file starts with a four number combination that is not 0000. ex. 2514.NC 
# Please open copy and past the link on the top of this page into a web browser which will take you to the streamlit site. 
# Click on the button that reads "Browse files", and chose the .NC file you want to get modified.
# The pragram will outute the the modified file with the same name. Please click the button "Download Modified File" To download your updated file. 
