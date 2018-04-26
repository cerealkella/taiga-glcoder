def parse_list(input_string):
    new_list = input_string.replace(" ", ""). \
        replace(";", ",").replace("|", ",").split(",")
    return new_list


amt_list = parse_list(amt)
gl_list = parse_list(gl)

if len(gl_list) == len(amt_list):
    i = 0
    gltext = ""
    while i < len(gl_list):
        gltext += gl_list[i] + " - $" + amt_list[i] + "\n"
        i += 1
    print(gltext)
else:
    print("List Lengths do not match")
