#   This file is part of TelegCam.
#
#    TelegCam is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.
#
#    TelegCam is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with TelegCam.  If not, see <https://www.gnu.org/licenses/>.

import urllib
import cv2

def get_frame(url):
    try:
        urllib.request.urlretrieve(url, "tutorial.mp4")
        vidcap = cv2.VideoCapture('tutorial.mp4')
        def getFrame(sec):
            vidcap.set(cv2.CAP_PROP_POS_MSEC,sec*1000)
            hasFrames,image = vidcap.read()
            if hasFrames:
                cv2.imwrite("image1.jpg", image)     # save frame as JPG file
            return hasFrames

        sec = 0
        frameRate = 0.5 # it will capture image in each 0.5 second
        count=1
        success = getFrame(sec)
        while success:
            count = count + 1
            sec = sec + frameRate
            sec = round(sec, 2)
            success = getFrame(sec)
        return 'successfully'
    except:
        return 'fail'

#для тестов
def try_get_frame(url, id):
    try:
        urllib.request.urlretrieve(url, f"0.mp4")
    except:
        print(url+';  ', str(id))