if __name__ == '__main__':
    with open("ai/data/data.txt", 'r') as inpf:

        # list of lines to write to output file
        lines = list()

        question = ""
        response = ""

        json = False
        for line in inpf.readlines():
            # if line is empty
            if line == "":
                continue
            
            # if we parse the json part
            if json:
                # if end of json
                if "}" in line:
                    response += "}"
                    lines.append(question + ";" + response + "\n")

                    # reset question and response
                    question = ""
                    response = ""

                    # end json parsing
                    json = False

                else:
                    response += line.strip()

            # if we start to parse the json now
            elif "{" in line:
                json = True
                response += "{"

            # no json = question line
            else:
                question = line.strip().replace('"', '')

        with open("ai/data/formatted_data_final.csv", 'w') as outf:
            outf.writelines(lines)
