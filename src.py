import os
import shutil
import datetime

# check environment
def init(musthave):
    dir=os.path.dirname(__file__)
    ls=os.listdir(dir)
    # checks if directories exists, if not: creats dirs
    for entry in musthave:
        if entry not in ls:
            print("Create directory " + entry)
            os.mkdir(dir + "/" + entry)     

# writing logfile
def log(message):
    workdir="log"
    filename="new_log"
    file=dir_env(workdir, filename)[2]
    with open(file, "a") as logfile:
        logfile.write(str(datetime.datetime.now()) + "  -  " + message + "\n")

# scan dir, return file list    
def scan_dir(workdir):
    filelist=[]
    # dir is the current directory of THIS script
    dir=os.path.dirname(__file__)
    # path is the path to scan for files
    path=str(dir) + "/" + workdir
    # scan dir for transcripts
    ls=os.scandir(path)
    # list all files in path
    for entry in ls:
        if entry.is_file() and not entry.name.startswith('.') and (entry.name.endswith('.txt') or entry.name.endswith('.html')) :
            filelist.append(entry.name)
        else:
            print("[WARNING]: scan_dir: Skipping " + entry.name)
            log("[WARNING]: scan_dir: Skipping " + entry.name)
    return filelist

# copy file
def cp_files(fromdir, todir, filename):
    # copy files to dir
    dir=os.path.dirname(__file__)
    fromdir = dir + "/" + fromdir + "/" + filename
    todir = dir + "/" + todir + "/" + filename
    try: 
        shutil.copy(fromdir, todir)
    except:
        print("[WARNING]: cp_files: copy file ", filename, " from ", fromdir, " to ", todir, " failed")
        log("[WARNING]: cp_files: copy file ", filename, " from ", fromdir, " to ", todir, " failed")

# create paths
def dir_env(workdir, filename):
    workenv=[]
    dir=os.path.dirname(__file__)
    # workenv[0] => speaker
    # workenv[1] => dir
    # workenv[2] => filename(incl path)
    # workenv[3] => filename_new (incl. path)
    workenv.append(filename.split('.')[0])
    workenv.append(os.path.dirname(__file__))
    workenv.append(dir + "/" + workdir + "/" + filename)
    workenv.append(dir + "/" + workdir + "/" + workenv[0] + "_new.txt")
    return workenv

# remove old file, rename new file
def cleanup(filename,filename_new):
    try: 
        os.remove(filename)
    except:
        print("[WARNING]: cleanup: Could not remove " + filename)
        log("[WARNING]: cleanup: Could not remove " + filename)
    
    try:
        os.rename(filename_new, filename)
    except:
        print("[WARNING]: cleanup: Could not move " + filename_new)
        log("[WARNING]: cleanup: Could not move " + filename_new)

# remove old files from directory
def clean_all(dir):
    for file in scan_dir(dir):
        filepath=dir_env(dir,file)[2]
        #print(filepath)
        try: 
            os.remove(filepath)
        except:
            print("[WARNING]: clean_all: Could not remove " + filename)
            log("[WARNING]: clean_all: Could not remove " + filename)

# manipulate trancript files
def edit_transcripts(workdir, f):
    ###
    # insert speaker name behind timestamps
    ###
    # separator
    separator = "] "
    # get speaker name
    speaker = dir_env(workdir, f)[0]
    substitution = separator + "<br><br><b>" + speaker + ":" + "</b>"
    # open transcript file 
    filename = dir_env(workdir, f)[2]
    filename_new = dir_env(workdir, f)[3]
    # write speaker to file
    with open(filename_new, "w") as newfile:
        with open(filename, "r") as myfile:
            for line in myfile:
                # insert speaker name behind timestamp
                newline = line.replace(separator, substitution)
                try:
                    newfile.write(newline)
                except:
                    print("[WARNING]: edit_transcripts: Unable to write to file " + newfile)
                    log("[WARNING]: edit_transcripts: Unable to write to file " + newfile)
    
    # remove old file, rename new file
    cleanup(filename, filename_new)

# remove double entries (errors from whisper)
def remove_doubles(workdir, f):
    # open transcript file 
    separator = "]"
    filename = dir_env(workdir, f)[2]
    filename_new = dir_env(workdir, f)[3]
    lastline = ""
    # check if multiple entries in a row with same content
    # write speaker to file
    with open(filename_new, "w") as newfile:
        with open(filename, "r") as myfile:
            for line in myfile:
                thisline = line.split(separator)[1]
                if thisline != lastline:
                    try:
                        newfile.write(line)
                    except:
                        print("[WARNING]: remove_doubles: Unable to write to file " + newfile)
                        log("[WARNING]: remove_doubles: Unable to write to file " + newfile)
                    
                    lastline = thisline
    
    # remove old file, rename new file
    cleanup(filename, filename_new)
    
# filter transcript 
def apply_filter(workdir, f, word):
    filename = dir_env(workdir, f)[2]
    filename_new = dir_env(workdir, f)[3]
    # remove lines matching the filter
    with open(filename_new, "w") as newfile:
        with open(filename, "r") as myfile:
            for line in myfile:
                if word not in line:
                    try:
                        newfile.write(line)
                    except:
                        print("[WARNING]: apply_filter: Unable to write to file " + newfile)
                        log("[WARNING]: apply_filter: Unable to write to file " + newfile)
    
    # remove old file, rename new file
    cleanup(filename, filename_new)                  

# define the timestamp as sorting criteria
def my_sort(line):
    separator = "]"
    line_fields = line.strip().split(separator)
    separator = " "
    keyword = line_fields[0].split(separator)[0]
    separator = "["
    keyword = keyword.replace(separator,'')
    return keyword

# merge transcripts
def merge_files(dir, outputdir):
    filename_new = dir_env(outputdir, "output.txt")[2]
    # check if multiple entries in a row with same content
    with open(filename_new, "a") as newfile:
        for file in scan_dir(dir):
            filepath=dir_env(dir, file)[2]
            with open(filepath,"r") as myfile:
                for line in myfile:
                    try:
                        newfile.write(line)     
                    except:
                        print("[WARNING]: merge_files: Unable to write to file " + newfile)
                        log("[WARNING]: merge_files: Unable to write to file " + newfile)
    
    file_sorted = dir_env(outputdir, "output.txt")[3]
    with open(file_sorted, "w") as sortedfile:
        with open(filename_new, "r") as file:
            content = file.readlines()
            content.sort(key=my_sort)
            for line in content:
                try:
                    sortedfile.write(line)
                except: 
                    print("[WARNING]: merge_files (sort): Unable to write to file " + sortedfile)
                    log("[WARNING]: merge_files (sort): Unable to write to file " + sortedfile)
    
    cleanup(filename_new, file_sorted) 

# substitute timestamps with speaker names
def substitute_timestamps(workdir, f):
    separator = "]"
    filename = dir_env(workdir, f)[2]
    filename_new = dir_env(workdir, f)[3]
    with open(filename_new, "w") as mynewfile:
        with open(filename, "r") as myfile:
            for line in myfile:
                deleteme = line.split(separator)[0]
                deleteme =  deleteme + "]"
                try:
                    mynewfile.write(line.replace(deleteme,''))
                except:
                    print("[WARNING]: substitute_timestamps: Unable to write to file " + mynewfile)
                    log("[WARNING]: substitute_timestamps: Unable to write to file " + mynewfile)

# merge lines with same speaker
def concat_speaker(workdir, f):
    filename = dir_env(workdir, f)[2]
    #print(filename)
    filename_new = dir_env(workdir, f)[3]
    #print(filename_new)
    lastline = ""
    separator = "/"
    with open(filename_new, "w") as newfile:
        with open(filename, "r") as myfile:
            for thisline in myfile:
                myspeaker = thisline.split(separator)[0] + "/b>"
                if myspeaker in lastline:
                    try:
                        newfile.write(thisline.replace(myspeaker,''))
                    except:
                        print("[WARNING]: concat_speaker: Unable to write to file " + newfile)
                        log("[WARNING]: concat_speaker: Unable to write to file " + newfile)
                else:
                    try:
                        newfile.write(thisline)
                    except:
                        print("[WARNING]: concat_speaker: Unable to write to file " + newfile)
                        log("[WARNING]: concat_speaker: Unable to write to file " + newfile)
                lastline = thisline
     
    # remove old file, rename new file
    cleanup(filename, filename_new)

# create html file from transcript
def create_html_body(workdir, f):
    filename = dir_env(workdir, f)[2]
    fromfile = filename + ".txt"
    tofile = filename + ".html"
    try:
        shutil.copy(fromfile, tofile)
    except:
        print("[WARNING]: create_html_body: Unable to copy file " + fromfile)
        log("[WARNING]: create_html_body: Unable to copy file " + fromfile)
   