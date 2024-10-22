import soundfile as sf
import time
import os
import graph
from pydub import AudioSegment
from pydub.playback import play
import threading
import signal
FILE_LOCATION = ""
FFMPEG_LOCATION = ""
AudioSegment.ffmpeg = FFMPEG_LOCATION
UPDATE_RATE = 0.01 # s

def main():
    dirname = os.path.dirname(__file__)
    filename = FILE_LOCATION
    audio = threading.Thread(target=playAndSyncAudio, args=(filename,))    

    global r, g, data, frame_count, extra_frames
    g = graph.asciiGraph(37, 141, (-1,1), 0.1, (0, 48000), 10000)
    r = sf.SoundFile(filename)
    extra_frames = 0
    
    g.show()
    g.plotString(0, 6, filename)

    time.sleep(1)
    
    data = r.read(r.frames)
    frame_count = 0

    audio.start()
    time.sleep(1)

    i = 0
    while frame_count < r.frames:
        pltdata = data[frame_count:frame_count+int(r.samplerate*(UPDATE_RATE)+extra_frames)]
        coordinates = g.translateSamplesToCoordinate(pltdata)
        if i % 3 == 0: g.clearGraphData() # build up plots, creates a smoother visual affect
        
        for coordinate in coordinates[0]:
            g.graphPlot(coordinate[1], coordinate[0],"*")
        for coordinate in coordinates[1]:
            g.graphPlot(coordinate[1], coordinate[0],"@")
        frame_count += int(r.samplerate*(UPDATE_RATE))+extra_frames 
        time.sleep(UPDATE_RATE)
        i += 1
    g.hide()
    print("done")

def playAndSyncAudio(filename):
    global r, frame_count, extra_frames
    CHECK_RATE_SECONDS = 10
    file = AudioSegment.from_file(filename, format="mp3")
    for i in range(0, round(file.duration_seconds*1000), CHECK_RATE_SECONDS*1000):
        display_pos = frame_count
        theoretical_pos = i*(r.samplerate/1000)
        if (theoretical_pos - display_pos) > 0: 
            # in the next minute double this amount of frames need to be made up by the display
            # num of extra frames to be displayed in 60s = (theoretical_pos - display_pos)
            # 60 seconds = 60*(1/UPDATE_RATE) = 6000 iterations per 60 seconds
            # number of additional frames per iteration = extra frames/6000
            extra_frames = round((theoretical_pos - display_pos)*2.75/(CHECK_RATE_SECONDS*(1/UPDATE_RATE)))
            if extra_frames < 35: extra_frames = 40
        else:
            extra_frames = -round(((display_pos - theoretical_pos)/2)/(CHECK_RATE_SECONDS*(1/UPDATE_RATE)))+40

        g.plotString(0, len(filename)+7, "exframe: " + str(extra_frames) + " dframe: " + str(display_pos) + " (" + str(display_pos*1/r.samplerate) + "s) tframe: " + str(theoretical_pos) + " (" + str(theoretical_pos*1/r.samplerate) + "s)")
        #print("exframe: " + str(extra_frames) + " dframe: " + str(display_pos) + " (" + str(display_pos*1/r.samplerate) + "s) tframe: " + str(theoretical_pos) + " (" + str(theoretical_pos*1/r.samplerate) + "s)")
        if i+(CHECK_RATE_SECONDS*1000) > len(file):
            play(file[i:len(file)])
        else:
            play(file[i:i+CHECK_RATE_SECONDS*1000])

def handle_exit():
    g.hide()
    exit(0)


signal.signal(signal.SIGINT, handle_exit)

if __name__ == "__main__": main()
