import os
import random
import face_recognition
import cv2
import sqlite3
import subprocess
import urllib3

def main():

    database = 'employees.db'
    conn = sqlite3.connect(database)

    employee_dict = generateUsers(conn)

    # Get a reference to webcam #0 (the default one)
    video_capture_0 = cv2.VideoCapture(0)
    video_capture_1 = cv2.VideoCapture(2)
    
    known_face_names = list()
    known_face_encodings = list()
    
    for filename in os.listdir('dataset'):
        known_face_names.append(employee_dict[filename.split('.')[0]])
        known_face_encodings.append(face_recognition.face_encodings(face_recognition.load_image_file('dataset/' + filename))[0])
     
    while True:
        process(conn, known_face_names, known_face_encodings, video_capture_0, True, "Entry")
        process(conn, known_face_names, known_face_encodings, video_capture_1, False, "Exit")
        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
    video_capture_0.release()
    video_capture_1.release()
    cv2.destroyAllWindows()
 
frames_unknown_in = 0
http = urllib3.PoolManager()

def process(conn, known_face_names, known_face_encodings, video_capture, setInOffice, identifier):
    global frames_unknown_in, http

    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True

    # Grab a single frame of video
    ret, frame = video_capture.read()

    if frame is None:
        return

    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            # If a match was found in known_face_encodings, just use the first one.
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
                markInOffice(conn, name, setInOffice)
            else:
                frames_unknown_in = frames_unknown_in + 1

            if len(face_encoding) == 0:
                frames_unknown_in = 0

            print(frames_unknown_in)

            if frames_unknown_in > 10:
                http.request('GET', 'http://localhost:9001/alert')
                say("An unknown person is in the office")
                frames_unknown_in = 0

            face_names.append(name)

    process_this_frame = not process_this_frame

    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Write some Text

    font = cv2.FONT_HERSHEY_SIMPLEX
    bottomLeftCornerOfText = (30, 70)
    fontScale = 2
    fontColor = (0, 0, 255)
    lineType = 2

    cv2.putText(frame, identifier,
                bottomLeftCornerOfText,
                font,
                fontScale,
                fontColor,
                4,
                lineType)

    # Display the resulting image
    cv2.imshow('Video'+identifier, frame)

voices = [
    'Moira',
    'Alex',
    'Samantha'
]

def say(message):
    subprocess.call(["say", message, "-v", random.choice(voices)])

def greet(name):
   global nick_greetings

   greetings = [
       'Hello',
       'Bonjour',
       'Greetings',
       'What about yee',
       'Good day',
       'I am heartily glad to see you',
       'A new face? Why, no, it is'
   ]

   phrase = random.choice(greetings)

   if name == "Nick Mifsud":
        phrase = random.choice(nick_greetings)

   say(phrase + ' ' + name)

nick_dismissals = [
    'Goodbye and remember your lego',
    'One at the National?',
    'Lost child in aisle 6, answers to the name of'
]

nick_greetings = [
    'Good-day, there is a lego delivery for you',
    'Did you go home last night at all?',
    '10:45 AM? I will update the records'
]

def dismiss(name):
    global nick_dismissals

    dismissals = [
        'Goodbye',
        'See you next Tuesday',
        'Wee half day?',
        'Good ridance',
        'It pleases me greatly to see the departing rear end of'
    ]

    phrase = random.choice(dismissals)

    if name == "Nick Mifsud":
        phrase = random.choice(nick_dismissals)

    say(phrase + ' ' + name)

def markInOffice(conn, name, inOffice):
    cur = conn.cursor()
    cur.execute('UPDATE employees SET inOffice = ? where name = ? and inOffice = ?', (inOffice, name, not inOffice))

    if cur.rowcount > 0:
        if inOffice:
            greet(name)
        else:
            dismiss(name)
    
        print(name + " is now " + ("" if inOffice else "not") + " in the office")

    conn.commit()
  

def generateUsers(conn):
    conn.row_factory = sqlite3.Row

    employee_dict = {}
    for user in conn.execute('SELECT * from employees').fetchall():
        (id, name, email, office) = user
        employee_dict[str(id)] = name

    return employee_dict

if __name__ == '__main__':
    main()

