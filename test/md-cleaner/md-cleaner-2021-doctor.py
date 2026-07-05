import re


def check_md_lines(read_path, write_path):
    try:
        with (
            open(write_path, "a", encoding="utf-8") as write_file,
            open(read_path, "r", encoding="utf-8") as read_file,
        ):
            for i, line in enumerate(read_file.readlines()):
                line_to_write = ""
                # Disease broader category
                if (re.match(r"^\#{2}\s*CHAPTER\s*\d+:", line.strip())):
                    line_to_write = re.sub(r"^\#{2}\s*CHAPTER\s*\d:\s*", "# ", line.strip())
                # Disease name
                elif (re.match(r"^\#{2}\s*(?:\d+\.)+", line.strip())):
                    print(line.strip())
                    line_to_write = re.sub(r"^\#{2}\s*(?:\d\.)*\s", "## ", line.strip())
                # Subsection
                elif (re.match(r"^\#{2}\s", line.strip())):
                    line_to_write = re.sub(r"^\#{2}\s", "### ", line.strip())

                else:
                    line_to_write = line.strip()

                # Write the line
                write_file.write(line_to_write + "\n")
    except FileNotFoundError:
        print("File not found.")


check_md_lines("./doctor.md", "./doctor-cleaned.md")
