from src import *

##################################################################################
# Variables
filters = ["[Musik]", "[Abspann]", "[Aspann]", "[Music]", "[Intro]", "[Husten]", "[Niesen]", "[Gähnen]", "[Outro]", "[Stille]", "[Silence]", "* Titelsong *", "[Pause]"]
musthave = ["orig", "input", "output", "log"]

##################################################################################
# check environment
init(musthave)

##################################################################################
# clean up workdirs
clean_all("input")
clean_all("output")

##################################################################################
# edit all separate tracks in orig-directory
for file in scan_dir("orig"):
    cp_files("orig", "input", file)
    edit_transcripts("input", file)
    remove_doubles("input", file)
    for word in filters:
        apply_filter("input", file, word)

##################################################################################
# merge tracks and edit complete file
merge_files("input", "output")
substitute_timestamps("output", "output.txt")
concat_speaker("output","output_new.txt")

##################################################################################
# post processing
create_html_body("output", "output_new")