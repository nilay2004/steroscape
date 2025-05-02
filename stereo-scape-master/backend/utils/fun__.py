import string
import random
import cv2
import numpy as np
import os



def saveAndExtractPoses(videoArr, outputFolder, size, emit, everyFrame=5):
    videoArr[0].save(videoArr[1])
    cap = cv2.VideoCapture(videoArr[1])
    frame_no = 0
    fileSizes = 0
    i = 0
    skipFrames = everyFrame 
    maxFrames = 60 * 30
    totalFrames = 0
    capFrames = cap.get(cv2.CAP_PROP_FRAME_COUNT) 
    if capFrames > maxFrames:
        totalFrames = maxFrames
    else:
        totalFrames = capFrames
    totalFrames = totalFrames / skipFrames
    while (cap.isOpened):
        ret, frame = cap.read()
        if frame_no % skipFrames == 0:
            i += 1 
            target = str(outputFolder+ f'/{i}.jpg')
            try:
                x = cv2.resize(frame, size)
                cv2.imwrite(target, x)
                fileSizes = fileSizes + os.path.getsize(target)
            except Exception as e:
                pass
            percent = i / totalFrames * 100
            if percent >= 100: 
                percent = 100
            if emit is not None:
                emit('progress', {'title': f'Extracting and Resizing video frame number ({i}): ', 'progress': percent, 'process': 'res_image'})

        frame_no += 1
        if frame_no > maxFrames:
            break
    cap.release()
    return outputFolder, fileSizes, i

def randomString(limit):
    s = string.ascii_lowercase + string.ascii_uppercase
    f = ''
    for i in range(limit):
        index = random.randint(0, len(s) - 1)
        f = f + s[index]
    return f

def resizeAndSave(file, path, size=(100, 100)):
    try:
        print(f"Resizing and saving {file.filename} to {path}")
        fs = file.stream
        fb = bytearray(fs.read())
        image = cv2.imdecode(np.array(fb), cv2.IMREAD_COLOR)
        if image is None:
            print(f"Error: Could not decode image {file.filename}")
            return path, 0
            
        rsi = cv2.resize(image, size)
        
        # Ensure directory exists
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        cv2.imwrite(path, rsi)
        file_size = os.path.getsize(path)
        print(f"Successfully saved {file.filename} to {path}, size: {file_size}")
        return path, file_size
    except Exception as e:
        print(f"Error in resizeAndSave: {e}")
        return path, 0

def deleteFilesAndFolder(dir, deleteFolder = False, deleteFiles=True):
    if os.path.exists(dir) and os.path.isdir(dir):
        try:
            for root, dirs, files in os.walk(dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        print(f"Deleted file: {file_path}")
                    except OSError as e:
                        print(f"Error deleting file {file_path}: {e.strerror}")
        except OSError as e:
            print(f"Error accessing directory {dir}: {e.strerror}")
    if not deleteFolder and deleteFiles:
        if os.path.exists(dir):
            try:
                os.remove(dir)
            except OSError as e:
                print(f"Error: {dir} : {e.strerror}")
        else:
            print(f"File not found: {dir}")

    if deleteFolder:
        if os.path.exists(dir):
            try:
                os.remove(dir)
            except OSError as e:
                print(f"Error: {dir} : {e.strerror}")
        else:
            print(f"File not found: {dir}")