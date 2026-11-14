# -*- coding: utf-8 -*-
"""Builder script to assemble PROGRESS_MEETING_PRESENTATION_GUIDE_EN.md"""

import os
from part0_header import HEADER_AND_TOC
from part1_coldstart import SECTION_1
from part2_fr01_fr02 import FR01_AND_FR02
from part2_fr03_fr08 import FR03_TO_FR08
from part3_targets import SECTION_3_TARGETS
from part4_to_6 import SECTION_4_TO_6
from part7_playbook import SECTION_7_PLAYBOOK

def build():
    parts = [
        HEADER_AND_TOC,
        SECTION_1,
        FR01_AND_FR02,
        FR03_TO_FR08,
        SECTION_3_TARGETS,
        SECTION_4_TO_6,
        SECTION_7_PLAYBOOK
    ]
    full_text = "\n".join(parts)
    
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "PROGRESS_MEETING_PRESENTATION_GUIDE_EN.md")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_text)
    
    print(f"Successfully written {len(full_text):,} characters to {output_path}")

if __name__ == "__main__":
    build()

