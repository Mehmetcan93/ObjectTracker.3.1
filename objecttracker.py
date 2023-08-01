import time

import cv2 as cv
import sys
import os
import pandas as pd
import xlsxwriter
import numpy as np
import matplotlib.pyplot as plt
from numpy.fft import fft
import csv
from tkinter import *
from PIL import Image, ImageTk
from imutils.video import VideoStream
import threading
from tkinter import filedialog
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure



(major_ver, minor_ver, subminor_ver) = cv.__version__.split('.')


class ObjectTracker:
    def __init__(self, video_path,  video_number, debug_path, debug, rec, threshold, VAR):

        self.DEBUG = debug
        print("debug path",debug_path)


        self.tracker_types = ['KCF', 'CSRT']
        self.tracker_type = self.tracker_types[1]
        self.fish_tracker = None
        self.cage_tracker = None
        self.fish_position = []
        self.cage_position = []
        self.analayzfish = []
        self.analayzcage = []
        self.bbox = None
        self.box = None
        self.video_path = video_path
        self.debug_path = debug_path
        self.video = None
        self.current_frame = None
        self.create_excel_file = False
        self.video_number = video_number
        self.fish_template = None
        self.max_correlation = None
        self.correlation_threshold = threshold
        self.record = rec
        self.interrupt_key = None  # it waits every 1ms an intetrupt from keyboard
        self.pressed_key = None   # it waits every 1ms an comand from keyboard (next,back,roi,quit)
        self.newvar = VAR
        self.var = None

    def create_tracker(self):
        """
        Creates opencv tracker object

        :return: empty
        """

        if int(minor_ver) < 3:

            self.fish_tracker = cv.Tracker_create(self.tracker_type)
            self.fish_tracker = cv.Tracker_create(self.tracker_type)
        else:

            if self.tracker_type == 'MIL':
                self.fish_tracker = cv.TrackerMIL_create()
                self.cage_tracker = cv.TrackerMIL_create()
            elif self.tracker_type == 'KCF':
                self.fish_tracker = cv.TrackerKCF_create()
                self.cage_tracker = cv.TrackerKCF_create()
            elif self.tracker_type == "CSRT":

                self.fish_tracker = cv.TrackerCSRT_create()
                self.cage_tracker = cv.TrackerCSRT_create()

    def initialize_tracker(self):
        """
        Reads one frame from Video Object,
        Requests bounding box for template from user,
        Initialize tracker object with selected template.

        :return: empty
        """
        print("################")
        print(self.video_path)
        print("################")
        self.video = cv.VideoCapture(self.video_path)
        #cv.namedWindow("Tracking", cv.WND_PROP_FULLSCREEN)







        print(f"Total Frame {int(self.video.get(cv.CAP_PROP_FRAME_COUNT))}")
        # it allocates list as total number of video frame
        self.fish_position = [0 for i in range(int(self.video.get(cv.CAP_PROP_FRAME_COUNT)))]
        self.cage_position = [0 for i in range(int(self.video.get(cv.CAP_PROP_FRAME_COUNT)))]
        self.analayzfish = [0for i in range(int(self.video.get(cv.CAP_PROP_FRAME_COUNT)))]
        self.analayzcage = [0 for i in range(int(self.video.get(cv.CAP_PROP_FRAME_COUNT)))]

        # Exit if video not opened.
        if not self.video.isOpened():

            print("Could not open video")
            sys.exit()

        # Read first frame.
        ok, self.current_frame = self.video.read()
        if not ok:
            print('Cannot read video file')
            sys.exit()

        cv.putText(self.current_frame, 'To select box press "SPACE" (First Fish !) ', (30, 30),cv.FONT_HERSHEY_SIMPLEX, 0.60, (0, 0, 0), 2)
        cv.putText(self.current_frame, 'To continue press "ESC"', (30, 55), cv.FONT_HERSHEY_SIMPLEX, 0.60, (0, 0, 0), 2)

        #cv.namedWindow(f"{self.video_number}. Video's Templates bu mu", cv.WND_PROP_FULLSCREEN)
        #cv.moveWindow(f"{self.video_number}. Video's Templates bu mu", 500, 100)

        # Define an initial bounding box
        # [Top_Left_X, Top_Left_Y, Width, Height]
        cv.namedWindow(f"{self.video_number}. Video's Templates", cv.WND_PROP_FULLSCREEN)
        self.bbox = cv.selectROIs(f"{self.video_number}. Video's Templates",
                                  img=self.current_frame, showCrosshair=True, fromCenter=True)

        self.stop = False

        cv.destroyWindow(f"{self.video_number}. Video's Templates")

        if len(self.bbox) == 2 :
            self.fish_tracker.init(self.current_frame, self.bbox[0])
            self.cage_tracker.init(self.current_frame, self.bbox[1])
        else:
            print("Error : Be sure that you select two box, fish and cage object separately !")
            sys.exit()



        self.get_template(self.current_frame)

    def update_tracker(self):
        """
        Main Function
        Updates Cage and Fish Tracker each cycle with new frame.
        Calls other functions each cycle. (get_template, calculate_correlation_coefficient, find_position)

        :return: empty
        """

        # Start from first frame
        _ = self.video.set(cv.CAP_PROP_POS_FRAMES, 0)
        self.one_shot = True
        self.var = 0
        v = 0
        self.name=0

        def changebutton():
            self.var=1
            self.rootnew.destroy()

        def changebutton2():
            self.var=2
            print(self.fish_position)

        def changebutton3():
            self.var=3
        def changebutton4():
            self.var=4
        def changebutton5():
            self.var=5
        def changebutton6():
            self.var=6
        def changebutton7():
            self.var=110

        def changebutton8():
            self.var = cv.waitKey(0)
            print("========")
            print(self.var)
            print("========")

        self.missingpart = [0 for i in range(int(self.video.get(cv.CAP_PROP_FRAME_COUNT)))]#mhmtcn
        def changemame(f):
            self.name= f



        def gui():
            def update_plot():
                ax.clear()
                ax.plot(self.fish_position)
                ax.plot(self.cage_position)
                canvas.draw()

            # Function to generate a random data point and update the array
            def generate_data():

                update_plot()
                # Schedule the next data generation after 1 second (1000 milliseconds)
                root.after(1000, generate_data)
            def buttonclicked():

                adsoyad = entry.get()

                changemame(f=adsoyad)

            class PlotThread(threading.Thread):
                def __init__(self, ax, canvas,fish_position,cage_position):
                    threading.Thread.__init__(self)
                    self.ax = ax
                    self.canvas = canvas
                    self.fish_position = fish_position
                    self.cage_position = cage_position

                    self.running = True

                def run(self):
                    while self.running:
                        # Generate a random array
                        array = self.fish_position
                        array1 = self.cage_position


                        # Clear the previous plot
                        self.ax.clear()

                        # Plot the array
                        self.ax.plot(array)
                        self.ax.plot(array1)

                        # Update the canvas
                        self.canvas.draw()


                def stop(self):
                    self.running = False

            root = Tk()
            self.rootnew = root
            canvas = Canvas(root, height=1000, width=600)
            canvas.pack()
            frame_ust = Frame(root, bg='#CDCDC0')
            frame_ust.place(relx=0, rely=0, relwidth=1, relheight=1)
            btnIniciar = Button(root, text="Finish", width=10,bg="black",fg="white",font="Arial 20 bold", command=changebutton)
            btnIniciar.place(x=400, y=20)
            btnc= Button(root, text="Stop",bg="black",fg="white", width=10,font="Arial 20 bold", command=changebutton2)
            btnc.place(x=20,y=20)
            btnx = Button(root, text="Continue", width=10, command=changebutton3)
            btnx.place(x=200, y=200)
            btny = Button(root, text="Back", width=10, command=changebutton4)
            btny.place(x=200, y=120)
            btnl = Button(root, text="Wanted", width=10, command=changebutton5)
            btnl.place(x=200, y=300)
            btnp = Button(root, text="Next", width=10, command=changebutton6)
            btnp.place(x=300, y=120)
            btnp = Button(root, text="New Roi", width=10, command=changebutton7)
            btnp.place(x=300, y=200)

            entry = Entry(master=root, relief=SUNKEN, borderwidth=3, width=12)
            entry.place(x=300, y=300)
            b1 = Button(root, text="Enter frame number", width=10, command=buttonclicked)
            """"text="Enter", bg="black", fg="white", font="Arial 20 bold","""
            b1.place(x=240, y=350)
            fig = Figure(figsize=(6, 4), dpi=100)
            ax = fig.add_subplot(111)
            canvas = FigureCanvasTkAgg(fig, master=root)
            canvas.get_tk_widget().place(x=0,y=400)

            plot_thread = PlotThread(ax, canvas,self.fish_position, self.cage_position)
            plot_thread.start()# this is thread of graph



            root.mainloop()



        t1 = threading.Thread(target=gui)



        print(self.newvar)
        def devami():
            v = 0


            while True:


                draw_circle_on_template = True  # when new template created flag prevent any drawing on it
                # Start timer
                timer = cv.getTickCount()
                previousnextparam = True

                # Read a new frame
                ok, self.current_frame = self.video.read()
                if not ok:
                    break

                # Update Cage and Fish Tracker
                ok1, self.bbox[0] = self.fish_tracker.update(self.current_frame)
                ok2, self.bbox[1] = self.cage_tracker.update(self.current_frame)

                self.calculate_correlation_coefficient()

                # Re-creating fish tracker each time correlation coefficient is smaller than threshold.
                if self.max_correlation < self.correlation_threshold:
                    ok1 = False
                # Re-creating fish tracker each time unsuccessful when detection or low correlation coefficient occur.
                if not ok1:
                    cv.putText(self.current_frame, 'Tracking failure detected, re-create        template !', (20, 20),
                               cv.FONT_HERSHEY_SIMPLEX, 0.75, (68, 105, 255), 2)
                    cv.putText(self.current_frame, '"FISH"', (460, 20),
                               cv.FONT_HERSHEY_SIMPLEX, 0.75, (255, 0, 0), 2)
                    cv.putText(self.current_frame, 'To select box press "SPACE"', (20, 45),
                               cv.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)
                    cv.putText(self.current_frame, f'Frame: {str(int(self.video.get(cv.CAP_PROP_POS_FRAMES)))}', (20, 80),
                               cv.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)

                    # Create new fish tracker
                    if self.tracker_type == "KCF":
                        self.fish_tracker = cv.TrackerKCF_create()
                    elif self.tracker_type == "CSRT":
                        self.fish_tracker = cv.TrackerCSRT_create()

                    # Define an initial bounding box
                    cv.namedWindow(f"{self.video_number}. Video's Templates", cv.WND_PROP_FULLSCREEN)
                    self.bbox[0] = cv.selectROI(windowName=f"{self.video_number}. Video's Templates",
                                                img=self.current_frame, showCrosshair=True, fromCenter=True)
                    cv.destroyWindow(winname=f"{self.video_number}. Video's Templates")

                    # Get new fish template
                    self.get_template(self.current_frame)
                    draw_circle_on_template = False


                    # Initialize and Update Fish Tracker
                    self.fish_tracker.init(self.current_frame, self.bbox[0])
                    ok1, self.bbox[0] = self.fish_tracker.update(self.current_frame)

                # Re-creating refuge tracker each time unsuccessful detection occur.
                if not ok2:
                    cv.putText(self.current_frame, 'Tracking failure detected, re-create           template !', (20, 20),
                               cv.FONT_HERSHEY_SIMPLEX, 0.75, (68, 105, 255), 2)
                    cv.putText(self.current_frame, '"REFUGE"', (460, 20),
                               cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
                    cv.putText(self.current_frame, 'To select box press "SPACE"', (20, 45),
                               cv.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)
                    cv.putText(self.current_frame, f'Frame: {str(int(self.video.get(cv.CAP_PROP_POS_FRAMES)))}',(20, 80),
                               cv.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)

                    # Create new cage tracker
                    if self.tracker_type == "KCF":
                        self.cage_tracker = cv.TrackerKCF_create()
                    elif self.tracker_type == "CSRT":
                        self.cage_tracker = cv.TrackerCSRT_create()

                    # Define an initial bounding box
                    cv.namedWindow(f"{self.video_number}. Video's Templates", cv.WND_PROP_FULLSCREEN)
                    self.bbox[1] = cv.selectROI(windowName=f"{self.video_number}. Video's Templates",
                                                img=self.current_frame, showCrosshair=True, fromCenter=True)
                    cv.destroyWindow(winname=f"{self.video_number}. Video's Templates")

                    # Initialize and Update Cage Tracker
                    self.cage_tracker.init(self.current_frame, self.bbox[1])
                    ok2, self.bbox[1] = self.cage_tracker.update(self.current_frame)

                # Draw Fish bounding box
                if ok1 and draw_circle_on_template:
                    # Fish Tracking success
                    p1 = (int(self.bbox[0][0]), int(self.bbox[0][1]))
                    p2 = (int(self.bbox[0][0] + self.bbox[0][2]), int(self.bbox[0][1] + self.bbox[0][3]))

                    cv.rectangle(self.current_frame, p1, p2, (255, 0, 0), 2, 1)
                    fish_head_point = (int(self.bbox[0][0] + self.bbox[0][2] / 2),
                                       int(self.bbox[0][1] + self.bbox[0][3] / 2))
                    cv.circle(self.current_frame, fish_head_point, 7, (255, 0, 0), -1)

                # Draw Cage bounding box
                if ok2:
                    # Cage Tracking success
                    p3 = (int(self.bbox[1][0]), int(self.bbox[1][1]))
                    p4 = (int(self.bbox[1][0]) + self.bbox[1][2]), int(self.bbox[1][1] + self.bbox[1][3])
                    cage_point = (int(self.bbox[1][0] + self.bbox[1][2] / 2), int(self.bbox[1][1] + self.bbox[1][3] / 2))

                    cv.rectangle(self.current_frame, p3, p4, (0, 0, 255), 2, 1)
                    cv.circle(self.current_frame, cage_point, 7, (0, 0, 255), -1)

                self.find_position()

                # Calculate Frames per second (FPS)
                fps = cv.getTickFrequency() / (cv.getTickCount() - timer)

                # Display tracker type on frame
                cv.putText(self.current_frame, self.tracker_type + " Tracker", (20, 20),
                           cv.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2)

                # Display FPS on frame
                cv.putText(self.current_frame, "FPS : " + str(int(fps)), (20, 80),
                           cv.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2)

                # Display correlation coefficient number
                cv.putText(self.current_frame, "Fish Correlation coefficient:  " + str(round(self.max_correlation, 4)),
                           (200, 45), cv.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)

                # Display Frame number
                cv.putText(self.current_frame, f'Frame: {str(int(self.video.get(cv.CAP_PROP_POS_FRAMES)))}', (20, 50),
                           cv.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2)

                # Display result
                cv.namedWindow("Tracking", cv.WND_PROP_FULLSCREEN)
                cv.imshow("Tracking", self.current_frame)

                self.interrupt_key = cv.waitKey(1) & 0xFF

                # Terminate program if t pressed
                if self.var == 1:
                    #--------------------FINISH CODE-------------------
                    self.store_positions()


                    break

                if self.interrupt_key == ord("h"):

                    print(self.video.get(cv.CAP_PROP_POS_FRAMES))
                    self.missingpart[v]= self.video.get(cv.CAP_PROP_POS_FRAMES)
                    print(self.missingpart)
                    v=v+1

                # Stops program if c pressed
                if self.var == 2 or self.interrupt_key == ord("c"):
                    #----------HERE IS THE STOP POINT-------------------
                    print("c pressed")
                    print('"r":select Roi, "n":next frame, "b":previous frame, "q":continue')
                    flag = True
                    indicator = True
                    draw_circle_on_template = False


                    while True:

                        next_frame = self.video.get(cv.CAP_PROP_POS_FRAMES)
                        curr_frame = next_frame - 1
                        previous_frame = curr_frame - 1

                        # Update Cage and Fish Tracker
                        ok1, self.bbox[0] = self.fish_tracker.update(self.current_frame)
                        ok2, self.bbox[1] = self.cage_tracker.update(self.current_frame)

                        self.calculate_correlation_coefficient()
                        # Draw Fish bounding box
                        if ok1 and draw_circle_on_template and previousnextparam:
                            # Fish Tracking success
                            p1 = (int(self.bbox[0][0]), int(self.bbox[0][1]))
                            p2 = (int(self.bbox[0][0] + self.bbox[0][2]), int(self.bbox[0][1] + self.bbox[0][3]))
                            cv.rectangle(self.current_frame, p1, p2, (255, 0, 0), 2, 1)
                            fish_head_point = (int(self.bbox[0][0] + self.bbox[0][2] / 2),
                                               int(self.bbox[0][1] + self.bbox[0][3] / 2))
                            cv.circle(self.current_frame, fish_head_point, 7, (255, 0, 0), -1)
                            previousnextparam = False

                        #draw_circle_on_template = True

                        # Draw Cage bounding box
                        if ok2 and draw_circle_on_template and previousnextparam:
                            # Cage Tracking success
                            p3 = (int(self.bbox[1][0]), int(self.bbox[1][1]))
                            p4 = (int(self.bbox[1][0]) + self.bbox[1][2]), int(self.bbox[1][1] + self.bbox[1][3])
                            cage_point = (int(self.bbox[1][0] + self.bbox[1][2] / 2),
                                          int(self.bbox[1][1] + self.bbox[1][3] / 2))
                            cv.rectangle(self.current_frame, p3, p4, (0, 0, 255), 2, 1)
                            cv.circle(self.current_frame, cage_point, 7, (0, 0, 255), -1)
                            previousnextparam = False

                        if flag:
                            flag = False
                        else:
                            self.find_position()

                            # Display tracker type on frame
                            cv.putText(self.current_frame, self.tracker_type + " Tracker", (20, 20),
                                       cv.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2)

                            # Display correlation coefficient number
                            cv.putText(self.current_frame,
                                       "Fish Correlation coefficient:  " + str(round(self.max_correlation, 4)),
                                       (300, 45), cv.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)

                            # Display Frame number
                            cv.putText(self.current_frame, f'Frame: {str(int(self.video.get(cv.CAP_PROP_POS_FRAMES)))}',
                                       (20, 50),
                                       cv.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2)

                        # Display result
                        cv.namedWindow("Tracking", cv.WND_PROP_FULLSCREEN)
                        cv.imshow("Tracking", self.current_frame)


                        cv.waitKey(1000)


                        if indicator==True:
                            # Exit if q pressed
                            #print("waiting")
                            if self.var == 3:
                                indicator = False
                                #-------------CONTINUE CODE---------------------

                                break

                            # Previous frame
                            elif self.var == 4:
                                #-----------PREVIOUS FRAME------------------
                                #print("b pressed")
                                self.video.set(cv.CAP_PROP_POS_FRAMES, previous_frame)

                                print(previous_frame)

                                # Read a new frame
                                ok, self.current_frame = self.video.read()
                                if not ok:
                                    break
                                print(int(self.video.get(cv.CAP_PROP_POS_FRAMES)))
                                self.var=2
                                draw_circle_on_template = True
                                previousnextparam = True


                            elif self.var == 5:
                                print("l pressed")

                                wanted_frame = int(self.name)-1
                                #print("burdayım")
                                print(wanted_frame)

                                self.video.set(cv.CAP_PROP_POS_FRAMES, wanted_frame)
                                # Read a new frame
                                ok, self.current_frame = self.video.read()
                                if not ok:
                                    break
                                print(int(self.video.get(cv.CAP_PROP_POS_FRAMES)))

                            # Next Frame
                            elif self.var == 6:
                                #--------------------NEXT FRAME-------------------
                                print("n pressed")
                                self.video.set(cv.CAP_PROP_POS_FRAMES, next_frame)
                                # Read a new frame
                                ok, self.current_frame = self.video.read()
                                if not ok:
                                    break
                                print(int(self.video.get(cv.CAP_PROP_POS_FRAMES)))
                                self.var = 2
                                draw_circle_on_template = True
                                previousnextparam = True

                            # Select Roi
                            elif self.var == 110:
                                print("Select new bound box!")
                                self.video.set(cv.CAP_PROP_POS_FRAMES, curr_frame)

                                # Read a new frame
                                ok, self.current_frame = self.video.read()

                                if not ok:
                                    break

                                # Create new fish tracker
                                if self.tracker_type == "KCF":
                                    self.fish_tracker = cv.TrackerKCF_create()
                                elif self.tracker_type == "CSRT":
                                    self.fish_tracker = cv.TrackerCSRT_create()

                                # Define an initial bounding box
                                cv.namedWindow(f"{self.video_number}. Video's Templates", cv.WND_PROP_FULLSCREEN)
                                self.bbox[0] = cv.selectROI(windowName=f"{self.video_number}. Video's Templates",
                                                            img=self.current_frame, showCrosshair=True, fromCenter=True)
                                cv.destroyWindow(winname=f"{self.video_number}. Video's Templates")

                                # Get new fish template
                                self.get_template(self.current_frame)
                                draw_circle_on_template = False

                                # Initialize and Update Fish Tracker
                                self.fish_tracker.init(self.current_frame, self.bbox[0])
                                ok1, self.bbox[0] = self.fish_tracker.update(self.current_frame)
                                break

                            else:
                                #print("Please enter valid key !!")
                                #print('"r":select Roi, "n":next frame, "b":previous frame, "q":continue')
                                flag = True
                # for Recording Purposes

                if self.record:

                    if self.one_shot:  # Creates just one times VideoWriter Object
                        self.result = cv.VideoWriter(self.video_path[:-4] + "_TRACK.avi", cv.VideoWriter_fourcc(*'XVID'), 25,
                                                (self.current_frame.shape[1], self.current_frame.shape[0]), isColor=True)
                        self.one_shot = False
                        print("recording")
                    self.result.write(self.current_frame)
            self.result.release()


        t2= threading.Thread(target=devami)
        t1.start()
        t2.start()
        t1.join()
        t2.join()


        self.video.release()
        cv.destroyAllWindows()



    def find_position(self):
        """
        Finds x positions of cage and fish objects.

        :return: empty
        """

        fish_x_position = self.bbox[0][0] + self.bbox[0][2] / 2
        cage_x_position = self.bbox[1][0] + self.bbox[1][2] / 2
        fish_y_position  =self.bbox[0][1] + self.bbox[0][3] / 2
        cage_y_position =self.bbox[1][1] + self.bbox[1][3] / 2
        if fish_x_position == 0.0:
            fish_x_position = -1000
        if cage_x_position == 0.0:
            fish_x_position = -1000

        print(f"{int(self.video.get(cv.CAP_PROP_POS_FRAMES))} : {fish_x_position}")
        print(f"{int(self.video.get(cv.CAP_PROP_POS_FRAMES))} : {cage_x_position}")# mid point of tracking area
        self.fish_position[int(self.video.get(cv.CAP_PROP_POS_FRAMES)) - 1] = fish_x_position
        self.cage_position[int(self.video.get(cv.CAP_PROP_POS_FRAMES)) - 1] = cage_x_position
        self.analayzfish[int(self.video.get(cv.CAP_PROP_POS_FRAMES)) - 1] = fish_y_position# yposition
        self.analayzcage[int(self.video.get(cv.CAP_PROP_POS_FRAMES)) - 1] = cage_y_position
        #print(self.fish_position)

    def store_positions(self):
        """
        Writes cage and fish positions to excel file.
worksheet = workbook.add_worksheet()
        content = ["Fish", "Cage"]
        columns_width = [6, 6]
        header_format = workbook.add_format({
            'font_color': 'black',
            'bold': 1,
            'font_size': 13,
            'align': 'left'
        })
        column = 0
        for item in content:
            worksheet.write(0, column, item, header_format)
            worksheet.set_column(column, column, columns_width[column])
            column += 1

        data = {
            "fish": self.fish_position,
            "refuge": self.cage_position
        }
        df = pd.DataFrame(data)
        df.to_excel(file_name, index=False)
        :return:
        """

        #file_name = os.path.join(self.csv_path)
       # workbook = xlsxwriter.Workbook(file_name)
        #object_header=["fish","cage"]

      #  print(self.video.get(cv.CAP_PROP_POS_FRAMES))



        raw_data = {'Fish': self.fish_position,
                    'Cage': self.cage_position}

        df = pd.DataFrame(raw_data, columns=['Fish',
                                             'Cage'])
        print(df)
        df.to_csv('Zebrafish.csv', index=False)

        raw_data = {'Fish': self.analayzfish,
                    'Cage': self.analayzcage,
                    'FishY': self.fish_position,
                    'CageY': self.cage_position}

        dx = pd.DataFrame(raw_data, columns=['Fish',
                                             'Cage',
                                             'FishY',
                                             'CageY'])
        print(dx)
        dx.to_csv('Zebrafishanalayz.csv', index=False)



         # 3. Write data to the file



    def start_offline_analysis(self, start=0, stop=1500):
        """
        Creates cage and fish position and theirs fft analyses

        :param start: start frame
        :param stop: stop frame
        :return: empty
        """
        # Time Domain Signals (Cage and Fish)
        cage_arr_np = np.array(self.cage_position, dtype="float32")
        fish_arr_np = np.array(self.fish_position, dtype="float32")

        crop_time = range(start, stop)
        N = len(cage_arr_np[crop_time,])
        Ts = 40e-3
        Fs = 1 / Ts
        t = np.arange(N) * Ts
        f = np.arange(0, N / 10) / N * Fs

        final_cropped_cage_signal = cage_arr_np[crop_time,] - np.mean(cage_arr_np[crop_time,])
        final_cropped_fish_signal = fish_arr_np[crop_time,] - np.mean(fish_arr_np[crop_time,])

        fig, (ax1) = plt.subplots(1, 1, figsize=(20, 10))
        ax1.set(xlabel="Time", ylabel="Cage and Fish Coordinate")
        fig.suptitle("Tracking Analysis", fontsize="xx-large")
        ax1.plot(t, final_cropped_cage_signal, color="r", label="refuge", linewidth=1.5)
        ax1.plot(t, final_cropped_fish_signal, color="b", label="fish", linewidth=1.5)
        ax1.legend()
        print("here123")
        if self.DEBUG:
            my_file = '1_Time_Domain_cage_vs_fish.jpg'

            fig.savefig(os.path.join(self.debug_path, my_file))
            #fig.savefig('1_Time_Domain_cage_vs_fish.jpg')
            plt.close(fig)
        else:
            plt.show()

        # Frequency Domain Signals (Cage and Fish)
        fft_complex_cage = fft(final_cropped_cage_signal, N)
        fft_abs_cage = np.abs(fft_complex_cage)
        fft_complex_fish = fft(final_cropped_fish_signal, N)
        fft_abs_fish = np.abs(fft_complex_fish)

        fig = plt.figure(figsize=(20, 10))
        _, _, _ = plt.stem(f, fft_abs_cage[:len(f), ], linefmt='red', markerfmt='Dr', bottom=1.1)
        _, _, _ = plt.stem(f, fft_abs_fish[:len(f), ], linefmt='black', markerfmt='ok', bottom=1.1)
        plt.legend(("refuge", "fish"))
        if self.DEBUG:
            my_file = '2_FFT_cage_vs_fish.jpg'


            #fig.savefig( '2_FFT_cage_vs_fish.jpg')
            fig.savefig(os.path.join(self.debug_path, my_file))
            plt.close(fig)
        else:
            plt.show()

    def get_template(self, frame):
        """
        Returns Estimated,Cropped fish object

        :param frame:
        :return: empty
        """

        # Getting Fish Template Operations
        yi = self.bbox[0][1]   # initial y position
        yf = yi + self.bbox[0][3]  # final y position
        xi = self.bbox[0][0]  # initial x position
        xf = xi + self.bbox[0][2]  # final x position
        self.fish_template = frame[yi:yf, xi:xf]


    def calculate_correlation_coefficient(self):
        """
        Calculate correlation coefficient user selected template and tracker estimated template

        :return: empty

        """
        self.corr=1


        yi = self.bbox[0][1]  # initial y position
        yf = yi + self.bbox[0][3]  # final y position
        xi = self.bbox[0][0]  # initial x position
        xf = xi + self.bbox[0][2]  # final x position

        #print(yi,yf,xi,xf)
        if xi<1 or xf>495 or yi<1 or yf>1023 :
            print("HEY FISH IS GOING")
            self.var = 2
            self.corr=0
        if self.corr==1:
            fish_match = cv.matchTemplate(self.current_frame[yi:yf+1, xi:xf+1], self.fish_template, cv.TM_CCOEFF_NORMED)
            (minVal, maxVal, minLoc, maxLoc) = cv.minMaxLoc(fish_match)
            self.max_correlation = maxVal



    def olay_yeri_inceleme(self):
        """
        Determine missing parts
        :return: empty
        """
        print("If there is any missing part press y if not press p button")
        self.new_key = cv.waitKey(0) & 0xFF

        while True:


            if self.new_key == ord('y'):
                print("yes pressed... Please enter missing frame")
                missing_frame = input()

                print(missing_frame)


                self.video.set(cv.CAP_PROP_POS_FRAMES, missing_frame)
                # Read a new frame
                self.missingframe = self.video.read()
            if self.new_key == ord('p'):
                break

    def video_loop(self):
        frame = self.current_frame.read()
        image = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

        self.image = Image.fromarray(image)
        self.photo = ImageTk.PhotoImage(
            self.image)  # assigned to class variable `self.photo` so it resolves problem with bug in PhotoImage
        self.panel.configure(image=self.photo)
        if not self.stop:
            self.window.after(40, self.video_loop)  # 40ms = 25FPS
            # self.window.after(25, self.video_loop)   # 25ms = 40FPS

    def on_close(self):
        self.stop = True
        self.current_frame.stop()
        self.window.destroy()

    def analayzingcsv(self):

        self.var=0


        self.analayzingvariable= True
        def changebutton():
            self.var=1
        def changebutton2():
            self.var=10
        def changebutton3():
            self.var=11
        def changebutton4():
            self.var=4
        def changebutton5():
            self.var=5
        #self.missingpart = [0 for i in range(int(self.video.get(cv.CAP_PROP_FRAME_COUNT)))]#mhmtcn
        def changemame(f):
            self.name= f
        def gui():

            def buttonclicked():

                adsoyad = entry.get()

                changemame(f=adsoyad)




            root = Tk()
            root.resizable(width=True, height=True)# if we dont want to resize window take command line this
            canvas = Canvas(root, height=1000, width=600)
            canvas.pack()
            frame_ust = Frame(root, bg='#CDCDC0')
            frame_ust.place(relx=0, rely=0, relwidth=1, relheight=1)
            btnIniciar = Button(root, text="Finish", width=10, bg="black", fg="white", font="Arial 20 bold",
                                command=changebutton)
            btnIniciar.place(x=400, y=20)
            btnc = Button(root, text="Stop", bg="black", fg="white", width=10, font="Arial 20 bold",
                          command=changebutton2)
            btnc.place(x=20, y=20)
            btnx = Button(root, text="Continue", width=10, command=changebutton3)
            btnx.place(x=200, y=200)
            btny = Button(root, text="Back", width=10, command=changebutton4)
            btny.place(x=200, y=120)
            btnl = Button(root, text="Wanted", width=10, command=changebutton5)
            btnl.place(x=200, y=300)


            entry = Entry(master=root, relief=SUNKEN, borderwidth=3, width=12)
            entry.place(x=300, y=300)
            b1 = Button(root, text="Enter frame number", width=10, command=buttonclicked)
            b1.place(x=240, y=350)


            root.mainloop()



        #t1 = threading.Thread(target=gui)
        #print("burdayim")

        def cont():
            def openFile():
                self.filepath = filedialog.askopenfilename(initialdir=r"C:\Users\Lenovo\PycharmProjects\Zebrafish",
                                                      title="Open file",
                                                      filetypes=(("CSV files", "*.csv"),
                                                                 ("all files", "*.*")))
                file = open(self.filepath, 'r')
                # print(file.read())
                dataset = pd.read_csv(self.filepath)

                #self.x = dataset.iloc[:, 2].values  # deeplabcut sonuçlarında 4. satırdan başlıyor
                #self.y = dataset.iloc[:, 3].values
                self.coor = dataset.iloc[2:, 0].values
                self.x = dataset.iloc[2:, 1].values #deeplabcut sonuçlarında 4. satırdan başlıyor
                self.y = dataset.iloc[2:, 2].values
                self.like = dataset.iloc[2:, 3].values

                self.cage = dataset.iloc[:,1].values



                file.close()

            self.video = cv.VideoCapture(self.video_path)


            print(self.video_path)
            if not self.video.isOpened():
                print("Could not open video")
                sys.exit()
            openFile()

            i=0


            while True:
                next_frame   = self.video.get(cv.CAP_PROP_POS_FRAMES)
                curr_frame = next_frame - 1
                previous_frame = curr_frame - 1

                # Read a new frame
                ok, self.current_frame = self.video.read()

                if not ok:
                    break


                point = (int(float(self.x[int(self.video.get(cv.CAP_PROP_POS_FRAMES)) - 1])),
                         int(float(self.y[int(self.video.get(cv.CAP_PROP_POS_FRAMES)) - 1])))




                cv.putText(self.current_frame, f'Frame: {str(int(self.video.get(cv.CAP_PROP_POS_FRAMES))-1)}', (20, 50),
                           cv.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2)
                cv.circle(self.current_frame, point, 7, (0, 0, 255), -1)
                cv.namedWindow("CSVVideo", cv.WND_PROP_FULLSCREEN)
                cv.imshow("CSVVideo", self.current_frame)






                self.interrupt_key = cv.waitKey(0) & 0xFF




                if self.interrupt_key == ord('p'):
                    break
                elif self.interrupt_key == ord("n"):
                    print("n pressed")
                    self.video.set(cv.CAP_PROP_POS_FRAMES, next_frame)
                    # Read a new frame
                    ok, self.current_frame = self.video.read()
                    if not ok:
                        break
                    print(i)
                    print(int(self.video.get(cv.CAP_PROP_POS_FRAMES)))
                    print(point)

                    i=i+1

                elif self.interrupt_key == ord('b'):
                    print("b pressed")
                    self.video.set(cv.CAP_PROP_POS_FRAMES, previous_frame)
                    # Read a new frame
                    ok, self.current_frame = self.video.read()
                    if not ok:
                        break
                    print(int(self.video.get(cv.CAP_PROP_POS_FRAMES)))
                    i=i-1

                elif self.interrupt_key == ord('c'):
                    print("Select new bound box!")
                    self.video.set(cv.CAP_PROP_POS_FRAMES, next_frame)

                    # Read a new frame
                    ok, self.current_frame = self.video.read()
                    cv.namedWindow(f"{self.video_number}. Video's Templates", cv.WND_PROP_FULLSCREEN)
                    self.box = cv.selectROI(windowName=f"{self.video_number}. Video's Templates",
                                                img=self.current_frame, showCrosshair=True, fromCenter=True)
                    cv.destroyWindow(winname=f"{self.video_number}. Video's Templates")

                    self.x[i]=self.box[0] + self.box[2] / 2 # y coordinates don't confuse
                    self.y[i]=self.box[1] + self.box[3]/ 2 # x coordinates
                    print("bura degisen frame olmalı",i)
                    print(self.x[i])
                    print(self.y[i])
                    #i=i+1
                    self.video.set(cv.CAP_PROP_POS_FRAMES, next_frame)
                else:
                    print("Please enter valid key !!")
                    self.video.set(cv.CAP_PROP_POS_FRAMES, next_frame)




                print("burası koddaki frame:",i)
                #cv.waitKey(1000)

                if i==1500:
                    break
            print("buraya geldim")
            with open(self.filepath, 'r') as dosya:
                # CSV dosyasını okuyucu nesnesiyle açın
                okuyucu = csv.reader(dosya)

                print(okuyucu)

                # Satırları okuyun ve sütunları değiştirerek yeni bir liste oluşturun
                yeni_veriler = []
                for satir in okuyucu:
                    # 2. ve 3. sütunları değiştirin
                    #print(satir[3])

                    #satir[0] = satir[0]
                    satir[0] = self.coor
                    satir[1]= self.x
                    satir[2]= self.y
                    satir[3] = self.like
                    #satir[3]= satir[3]

                    # Değiştirilmiş satırı yeni verilere ekleyin
                    yeni_veriler.append(satir)
                raw_data = {'coords': satir[0],
                            'x': satir[1],
                            'y': satir[2],
                            'likelihood': satir[3]}

                dx = pd.DataFrame(raw_data, columns=['coords',
                                                     'x',
                                                     'y',
                                                     'likelihood'])
                print(dx)


                self.newfilepath = os.path.basename(os.path.normpath(self.filepath))
                print(self.newfilepath)
                dx.to_csv(self.newfilepath, index=False)




        cont()
        #t2 = threading.Thread(target=cont)
        #t1.start()

        #t2.start()
        #t1.join()
        #t2.join()




