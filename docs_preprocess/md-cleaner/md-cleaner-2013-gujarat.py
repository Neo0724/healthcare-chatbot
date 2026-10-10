import re


def check_md_lines(read_path, write_path):
    # Level 1 header
    main_header = [
        "COMMON CONDITIONS",
        "EMERGENCY CONDITIONS",
        "CARDIOVASCULAR DISEASES",
        "CENTRAL NERVOUS SYSTEM DISEASES",
        "GENITOURINARY DISEASES",
        "ENDOCRINE DISEASES",
        "GASTROINTESTINAL DISEASES",
        "INFECTIONS",
        "ENT DISEASES",
        "EYE DISEASES",
        "SKIN DISEASES",
        "OBSTETRICS AND GYNECOLOGY",
        "PSYCHIATRY DISORDERS",
        "ORTHOPEDIC CONDITIONS",
        "SURGERY",
        "RESPIRATORY DISEASES",
        "PEDIATRICS",
        "DENTAL CONDITIONS",
    ]

    try:
        with (
            open(write_path, "a", encoding="utf-8") as write_file,
            open(read_path, "r", encoding="utf-8") as read_file,
        ):
            for i, line in enumerate(read_file.readlines()):
                line_to_write = ""
                # Either level 1 or 2 header
                if line.strip().startswith("##") and line.strip().isupper():
                    # Level 1 header
                    if re.sub(r"^\#+\s+", "", line.strip()) in main_header:
                        line_to_write = re.sub(r"^\#", "", line.strip())
                    else:
                        # Level 2 header
                        line_to_write = line.strip()

                elif re.match(r'^\#+\s*Chapter\s*[0-9]', line.strip()):
                    print(line.strip())
                    line_to_write = ""

                elif line.strip().startswith("##"):
                    # Level 3 header
                    line_to_write = re.sub(r"^\#+\s*", "### ", line.strip())
                    
                else:
                    line_to_write = line.strip()

                # Write the line
                write_file.write(line_to_write + "\n")
    except FileNotFoundError:
        print("File not found.")


check_md_lines(
    "./standard-treatment-guidelines.md", "./standard-treatment-guidelines-cleaned.md"
)
