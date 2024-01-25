import cv2
import tkinter as tk
from tkinter.simpledialog import Dialog, askstring
from PIL import Image, ImageTk
import os
import sqlite3
from datetime import datetime

class MultiEntryDialog(Dialog):
    def __init__(self, parent, title, prompts):
        self.prompts = prompts
        Dialog.__init__(self, parent, title)

    def body(self, master):
        self.entries = []
        for prompt in self.prompts:
            tk.Label(master, text=prompt).pack()
            entry = tk.Entry(master)
            entry.pack()
            self.entries.append(entry)
        return self.entries[0]  

    def apply(self):
        self.result = [entry.get() for entry in self.entries]

class FaceCaptureApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Face Detection and Information Entry")

        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        self.canvas = tk.Canvas(self.master, width=1280, height=720, bg='white')
        self.canvas.pack()

        self.capture_button = tk.Button(self.master, text="Capture New Face", command=self.capture_face,
                                        bg='blue', fg='white', font=('Helvetica', 12), padx=10, pady=5)
        self.capture_button.pack(pady=10)

        self.is_capturing = False

        self.db_connection = sqlite3.connect('captured_faces.db')
        self.cursor = self.db_connection.cursor()

        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS captured_faces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                surname TEXT NOT NULL,
                phone TEXT NOT NULL,
                face_path TEXT NOT NULL,
                capture_time TEXT NOT NULL
            )
        ''')
        self.db_connection.commit()

        self.update()

    def capture_face(self):
        self.is_capturing = True

    def detect_face(self, frame):
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            face_roi = frame[y:y+h, x:x+w]
            if self.is_capturing:
                self.show_face_window(face_roi)

    def show_face_window(self, face_roi):
        rgb_image = cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(rgb_image)
        image = ImageTk.PhotoImage(image)

        prompts = ["Enter Name:", "Enter Surname:", "Enter Phone Number:"]
        dialog = MultiEntryDialog(self.master, "Enter Information", prompts)
        user_info = dialog.result

        if user_info:
            user_name, user_surname, user_phone = user_info
            self.save_face_and_info(face_roi, user_name, user_surname, user_phone)
            self.is_capturing = False
            
    def save_face_and_info(self, face_roi, user_name, user_surname, user_phone, save_path='captured_faces'):
        os.makedirs(save_path, exist_ok=True)
        face_filename = f"{user_name}_{user_surname}_face.jpg"
        face_filepath = os.path.join(save_path, face_filename)
        cv2.imwrite(face_filepath, face_roi)

        capture_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        query = '''
            INSERT INTO captured_faces (name, surname, phone, face_path, capture_time)
            VALUES (?, ?, ?, ?, ?)
        '''
        values = (user_name, user_surname, user_phone, face_filename, capture_time)
        self.cursor.execute(query, values)
        self.db_connection.commit()

        print(f"Face captured for {user_name} {user_surname}. Image saved at: {face_filepath}")


    def update(self):
        ret, frame = self.cap.read()
        self.detect_face(frame)

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(rgb_image)
        image = ImageTk.PhotoImage(image)

        self.canvas.create_image(0, 0, anchor=tk.NW, image=image)
        self.canvas.image = image

        self.master.after(10, self.update)

    def __del__(self):
        self.cap.release()
        self.db_connection.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceCaptureApp(root)
    root.mainloop()