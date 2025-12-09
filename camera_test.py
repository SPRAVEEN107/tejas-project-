import cv2
import numpy as np
import insightface
from pymongo import MongoClient
from numpy.linalg import norm
from datetime import datetime
import warnings
import openpyxl
import os

warnings.filterwarnings("ignore")

# -------------------------------------------------------
# CONFIG
# -------------------------------------------------------
MONGO_URI = "mongodb+srv://praveen:yourstrongpassword123@attendancedb.tpwmjgs.mongodb.net/?appName=AttendanceDB"
CTX_ID = -1                    # CPU mode only
ARC_THRESHOLD = 0.38           # Recommended for ArcFace CPU

# -------------------------------------------------------
# LOAD ARC FACE MODEL
# -------------------------------------------------------
print("Loading ArcFace model (CPU mode)...")
model = insightface.app.FaceAnalysis(name="buffalo_l")
model.prepare(ctx_id=CTX_ID, det_size=(640, 640))

# -------------------------------------------------------
# COSINE SIMILARITY
# -------------------------------------------------------
def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (norm(a) * norm(b)))

# -------------------------------------------------------
# LOAD STUDENT ENCODINGS
# -------------------------------------------------------
def load_encodings():
    client = MongoClient(MONGO_URI)
    db = client["AttendanceDB"]
    col = db["students"]

    names = []
    rolls = []
    encodings = []

    for doc in col.find({"model": "arcface"}):
        names.append(doc["name"])
        rolls.append(doc["rollNo"])
        encodings.append(np.array(doc["face_encoding"], dtype=float))

    print(f"Loaded {len(encodings)} ArcFace encodings from DB.")
    return names, rolls, encodings

names_list, rolls_list, known_embeddings = load_encodings()

# -------------------------------------------------------
# PREVENT MULTIPLE MARKINGS
# -------------------------------------------------------
marked_students = set()
already_displayed = set()

# -------------------------------------------------------
# CREATE TODAY'S EXCEL FILE
# -------------------------------------------------------
today = datetime.now().strftime("%Y-%m-%d")
excel_file = f"attendance_{today}.xlsx"

if not os.path.exists(excel_file):
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.append(["Roll No", "Name", "Timestamp"])
    wb.save(excel_file)
    print(f"📁 Created file: {excel_file}")

# -------------------------------------------------------
# ADD ROW TO EXCEL
# -------------------------------------------------------
def add_to_excel(roll, name):
    wb = openpyxl.load_workbook(excel_file)
    sheet = wb.active
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append([roll, name, now])
    wb.save(excel_file)

# -------------------------------------------------------
# CAMERA LOOP
# -------------------------------------------------------
cap = cv2.VideoCapture(0)
print("\nCamera started... press 'q' to quit\n")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    faces = model.get(frame)

    for face in faces:
        emb = face.embedding
        emb = emb / np.linalg.norm(emb)

        sims = [cosine_similarity(emb, kb) for kb in known_embeddings]
        best_idx = int(np.argmax(sims))
        best_score = sims[best_idx]

        x1, y1, x2, y2 = face.bbox.astype(int)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)

        if best_score > ARC_THRESHOLD:
            name = names_list[best_idx]
            roll = rolls_list[best_idx]
            label = f"{name} ({roll})"

            if roll not in marked_students:
                add_to_excel(roll, name)
                marked_students.add(roll)
                print(f"✔ Marked: {name} ({roll})")

            else:
                if roll not in already_displayed:
                    print(f"⚠ {name} ({roll}) already marked.")
                    already_displayed.add(roll)

        else:
            label = "Unknown"

        cv2.putText(frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

    cv2.imshow("ArcFace Attendance System", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("\n📁 Attendance saved successfully!")
