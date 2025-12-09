const fs = require('fs');
const path = require('path');
const mongoose = require('./db');
const Student = require('./models/student');

async function bulkInsert() {
  await require('./db'); // ensure DB connection

  try {
    // Load JSON file (make sure students.json is in root folder)
    const dataPath = path.join(__dirname, 'students.json');
    const rawData = fs.readFileSync(dataPath);
    const students = JSON.parse(rawData);

    for (const student of students) {
      const created = await Student.create({
        name: student.name,
        email: student.email,
        face_encoding: student.face_encoding
      });
      console.log(`✅ Inserted: ${created.rollNo} - ${created.name}`);
    }

    console.log('🎉 Bulk insert completed successfully');
    process.exit(0);
  } catch (err) {
    console.error('❌ Error during bulk insert:', err);
  }
   finally {
    // Automatically close Mongoose connection
     {
      console.log('🔒 MongoDB connection closed');
    };
    process.exit(1); 
  }
}
bulkInsert();
