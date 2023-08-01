# ----------------------------------------------------------------------------------
# Template Matching Based Fully Automated Fast Ghost Fish Tracking Project - Main Function
# Created on : 24.09.2022
# Updated on : 01.08.2023
# Author     : Mehmet Yücel Sarıtaş, Mehmetcan Gökçe
# Version    : 3.1
# ----------------------------------------------------------------------------------
import shutil
from objecttracker import ObjectTracker
import os
import xlsxwriter
from pathlib import Path
from tkinter import *
import threading
from tkinter.filedialog import askdirectory
from tkinter import filedialog

# ----------------------------------------------------------------------------------
# MULTIPLE FILES ANALYSIS PARAMETERS
# ----------------------------------------------------------------------------------
multi_main_folder_name = r"C:/Users/Lenovo/PycharmProjects/Zebrafish/örn"            #For multiple tracking, you should put the file path of the videos here.
# ----------------------------------------------------------------------------------
# MAIN PARAMETERS
# ----------------------------------------------------------------------------------
SINGLE_FILE_ANALYSIS = True # To test only one file or Whole Folder
REC = True  # To enable video recording
EXCEL_WRITE = True  # To enable extract cage and fish information to excel
DEBUG = True
isFFT = True
CORRELATION_THRESHOLD = 0.1  # it takes number between 0 and 1
video_format = "avi"
excel_format = "xlsx"
video_paths = []  # To hold path of each video
excel_path = []   # The path that excel files will be created
debug_path = []  # The path where fft and position graphs are created
root_paths = []
template_trackers = []  # To hold each template_matching object
var=0
AnalayzingCSV= False

def single_file_analysis():




    def get_folder_path():

        global file_path
        global debug_path


        file_path = filedialog.askopenfile(mode='r', filetypes=[('Video Files', '*.avi')]) # bu kısım ayrı bir gui açıyor durduk yere



        if file_path:

            path = file_path.name
            print(path)
            file_path.close()

            print("selected file:",path)
            file_path = path





        debug_path = askdirectory()
        if debug_path:
            print("selected debug path:", debug_path)
            #root.destroy()



    get_folder_path()

    print("file path altta yazcak")
    print(file_path)
    template_matching = ObjectTracker( file_path, 1 ,debug_path, debug=DEBUG, rec=REC, threshold=CORRELATION_THRESHOLD,VAR=var)
    if AnalayzingCSV:

        template_matching.analayzingcsv()
    else:
        template_matching.create_tracker()
        template_matching.initialize_tracker()
        template_matching.update_tracker()
        template_matching.start_offline_analysis()
        if EXCEL_WRITE:
            template_matching.store_positions()


t2 = threading.Thread(target=single_file_analysis)
def multiple_file_analysis():
    # file count and clean all files except raw files -------------------------------

    file_count = 0
    for (root, dirs, files) in os.walk(multi_main_folder_name, topdown=True):
        for file in files:
            if file.endswith(".avi") and not (file.endswith("_TRACK.avi")):
                file_count = file_count + 1
                # print(root + "/" + file)
            elif file.endswith(".log") or file.endswith("tracker.xlsx") \
                    or file.endswith("_TRACK.xlsx") \
                    or file.endswith("_TRACK.avi"):
                os.remove(os.path.join(root, file))
    total_files = file_count
    print("Total Files:", total_files)

    # main loop --------------------------------------------------------------------
    for (root, dirs, files) in os.walk(multi_main_folder_name, topdown=True):


        for file in files:


            if file.endswith(".avi") and not (file.endswith("_TRACK.avi")):



                file_path = os.path.join(root, file[:])
                f_name = file[:-4]  # to be consistent with the One File Test Analysis
                excel_path.append(os.path.join(root, f_name + "_TRACK.xlsx"))
                video_paths.append(file_path)
                root_paths.append(root)



    # Debug Folder
    for _ in range(len(video_paths)):



        debug_path.append(os.path.join(video_paths[_][:-4] + "_DEBUG/"))



        if DEBUG:


            if os.path.exists(debug_path[_]):

                shutil.rmtree(debug_path[_])

            os.makedirs(debug_path[_])

    # Create Template Objects for multiple tracking
    # Driver Functions

    for _ in range(len(video_paths)):


        template_matching = ObjectTracker(video_paths[_], video_number=_ + 1, debug_path=debug_path[_],
                                          debug=DEBUG, rec=REC, threshold=CORRELATION_THRESHOLD,VAR=var)
        template_matching.create_tracker()

        template_matching.initialize_tracker()
        template_trackers.append(template_matching)

    for _ in range(len(video_paths)):
        template_trackers[_].update_tracker()
        template_trackers[_].start_offline_analysis()
        if EXCEL_WRITE:
            template_trackers[_].store_positions()

    file_count = 0
    # ------------------------ TRACKER INFO/LOG -------------------------------------------
    for _ in range(len(video_paths)):
        file_count += 1
        p = Path(video_paths[_])
        cond_name = p.parts[-4]
        light_name = p.parts[-3]
        cage_name = p.parts[-2]
        file = p.parts[-1]
        file_path = video_paths[_]
        track_path = os.path.join(video_paths[_][:-4] + "_TRACK.avi")

        # tracker LOG
        worksheet.write(file_count, 0, file_count, text_format)
        worksheet.write_url(file_count, 1, root_paths[_], string="Open folder ->")
        worksheet.write(file_count, 2, cond_name, text_format)
        worksheet.write(file_count, 3, light_name, text_format)
        worksheet.write(file_count, 4, cage_name, text_format)
        worksheet.write(file_count, 5, file, text_format)
        worksheet.write_url(file_count, 6, file_path, string="Watch video ->")
        worksheet.write_url(file_count, 7, track_path, string="Watch tracker ->")
        worksheet.write_url(file_count, 8, excel_path[_], string="Open data ->")
        worksheet.write_url(file_count, 9, debug_path[_], string="Open folder ->")

    workbook.close()


if SINGLE_FILE_ANALYSIS:


    single_file_analysis()



else:
    file_name = os.path.join(multi_main_folder_name, 'tracker.xlsx')
    workbook = xlsxwriter.Workbook(file_name)
    worksheet = workbook.add_worksheet()
    content = ["Num", "Main Folder", "Cond", "Light", "Cage", "File Name",
               "Raw Video", "Tracker Video", "Track Data", "Debug Folder"]
    columns_width = [6, 14, 8, 8, 16, 78,
                     14, 15, 12, 15]
    header_format = workbook.add_format({
        'font_color': 'black',
        'bold': 1,
        'font_size': 13,
        'align': 'left'
    })
    text_format = workbook.add_format({
        'font_color': 'black',
        'font_size': 12,
        'align': 'left'
    })
    column = 0
    for item in content:
        worksheet.write(0, column, item, header_format)
        worksheet.set_column(column, column, columns_width[column])
        column += 1

    try:
        multiple_file_analysis()
    except:

        workbook.close()
