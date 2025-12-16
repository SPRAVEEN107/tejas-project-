Python 3.10 or 3.11
"pip install insightface onnxruntime opencv-python numpy pymongo python-dotenv openpyxl"
"pip install onnxruntime-gpu"(if you want only )


NOTE:IF YOU GOT CV2 ERROR THEN USE 
"pip uninstall opencv-python opencv-contrib-python -y"
"pip install opencv-python"


"python camera_test.py" to run the camera live feed 
"python create_encodings.py" to make the face encodings 
"python log_attendance.py" to get the list of students present or absentes list 
"node Bulkinsert.js " to insert the students into the database (mongoDB atlas)
