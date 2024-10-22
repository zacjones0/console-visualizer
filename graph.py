import threading
import numpy as np
import os
import math

class asciiGraph:
    def __init__(self, height, width, ylim, ytick, xlim, xtick):
        self.graph_height = height
        self.graph_width = width
        self.graph_ylim = ylim
        self.graph_ytick = ytick
        self.graph_xlim = xlim
        self.graph_xtick = xtick


        os.system("mode con lines=%s cols=%s" %(str(100), str(150)))
        self.screen_height = 37
        self.screen_width = 141
        self.screen_data = np.full((self.screen_height, self.screen_width), " ")
        self.graph_data = np.full((self.screen_height, self.screen_width), " ")
        self.screen = False

    def clearGraphData(self):
        self.graph_data = np.full((self.screen_height, self.screen_width), " ")
        return
    def clearScreenData(self):
        self.screen_data = np.full((self.screen_height, self.screen_width), " ")
    
    def _mergeScreenAndGraph(self, srow, grow):
        nrow = [" "]*len(srow)
        for i in range(0, len(srow)):
            if srow[i] == " " and grow[i] != " ":
                nrow[i] = grow[i]
            else: 
                nrow[i] = srow[i]
        return nrow

    def _screen(self):
        self.screen = True
        self._escapeSequence("[?47h") # save screen
        self._escapeSequence("[?25l") # hide cursor
        self._escapeSequence("[2J")
        while self.screen:
            self._escapeSequence("[H") # row 0 col 0
            for cursor_y in range(0, len(self.screen_data)):
                print(''.join(self._mergeScreenAndGraph(self.screen_data[cursor_y], self.graph_data[cursor_y])))
        return

    def _createYAxis(self):
        if self.graph_height > self.screen_height: raise ValueError("Graph height greater than screen height")
        
        for y in range(0, self.graph_height):
            if y == 0:
                # graph top limit
                self.plot(y, 0, "┼")
                self.plotString(y, 2, "(%s)" %str(self.graph_ylim[1]))
            elif y == self.graph_height-1:
                # graph bottom limit
                self.plot(y, 0, "┼")
                self.plotString(y, 2, "(%s)" %str(self.graph_ylim[0]))
            elif y == round(self.graph_height/2):
                self.plot(y, 0, "┼")
                self.plotString(y, 2, "(0)")
            
            else:
                self.plot(y, 0, "│")
        

    def _createXAxis(self):    
        if self.graph_width > self.screen_width: raise ValueError("Graph width greater than screen width")
        center_y = int(self.graph_height/2)

        # find how many chars apart each tick is
        xtickCharLength = int(self.graph_width/(self.graph_xlim[1]/self.graph_xtick))
        for x in range(0, self.graph_width):
            if x != 0:
                if x % xtickCharLength == 0:
                    self.plot(center_y, x, "┼")
                    tickLabel = str(int(self.graph_xtick*(x/xtickCharLength)))
                    self.plotString(center_y+1, x-math.floor(len(tickLabel)/2), tickLabel)
                else:
                    self.plot(center_y, x, "─")
        self.plot(center_y, 0, "┼")
        return 

    def show(self):
        self._createYAxis()
        #self._createXAxis()
        self.screen_thread = threading.Thread(target=self._screen)
        self.screen_thread.start()
        return
    
    def hide(self):
        self.screen = False
        self._escapeSequence("[2J") # clear screen
        self._escapeSequence("[?25h") # show cursor
        self._escapeSequence("[?47l") # restore screen
        return
    
    def _escapeSequence(self, code):
        print("\x1b%s" %code, end='')
        return
    
    def plot(self, y,x,char):
        self.screen_data[y][x] = char
        return
    
    def plotString(self, sy, sx, string, wraplength=None):
        relx = sx
        rely = sy
        for char in string:
            self.plot(rely, relx, char)
            relx+=1
            if wraplength != None:
                if rely == wraplength:
                    rely += 1
                    relx = sx
        return
    
    def graphPlot(self, y,x,char):
        self.graph_data[y][x] = char
        return
    
    def translateSamplesToCoordinate(self, data):
        numAvailableCharsOnXAxis = self.screen_width
        # debug
        #print("num available chars on x axis: " + str(numAvailableCharsOnXAxis))
        #print("num of samples: " + str(len(data)))
        numSamplesToBeAveragedPerChar = math.ceil(len(data)/numAvailableCharsOnXAxis)
        #print("num samples to be averaged per char:" + str(numSamplesToBeAveragedPerChar))
        results = [[], []]
        for i in range(0, len(data), numSamplesToBeAveragedPerChar):
            total_lc = 0 # left channel
            total_rc = 0 # right channel
            numSamples = numSamplesToBeAveragedPerChar
            for j in range(0, numSamplesToBeAveragedPerChar):
                if i+j > len(data)-1:
                    numSamples -= 1
                    continue
                total_lc += data[i+j][0]
                total_rc += data[i+j][1]

            # minus symbol is down, plus is up, therefore flip the sign
            averageMovement_lc = -(total_lc/numSamples)*round(self.screen_height/2)
            averageYCoord_lc = round(round(self.screen_height/2)+averageMovement_lc)
            # check range
            if averageYCoord_lc > self.screen_height-1: averageYCoord_lc = self.screen_height-1
            if averageYCoord_lc < 0: averageYCoord_lc = 0
            
            averageMovement_rc = -(total_rc/numSamples)*round(self.screen_height/2)
            averageYCoord_rc = round(round(self.screen_height/2)+averageMovement_rc)
            # check range
            if averageYCoord_rc > self.screen_height-1: averageYCoord_rc = self.screen_height-1
            if averageYCoord_rc < 0: averageYCoord_rc = 0
            
            # debug
            #print("center y:" + str(round(self.screen_height/2)) + "    ave movement: " + str(averageMovement))
            #print("x:" + str(round(i/numSamplesToBeAveragedPerChar)) + "   y:" + str(round(averageYCoord)))
            results[0].append([round(i/numSamplesToBeAveragedPerChar), averageYCoord_lc])
            results[1].append([round(i/numSamplesToBeAveragedPerChar), averageYCoord_rc])
        return results