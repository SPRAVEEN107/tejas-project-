const Student = require('./models/student');

async function addStudent() {
  await require('./db'); // ensure DB connected

  try {
    const s = await Student.findOneAndUpdate(
      { rollNo: '24EG107B49' }, // search by rollNo
      {
        name: 'PRAVEEN',
        email: 'PRAVEEN@example.com',
        face_encoding: Array(128).fill(0.2)
      },
      {
        new: true,   // return the updated document
        upsert: true, // insert if not found
        setDefaultsOnInsert: true
      }
    );

    console.log('✅ Student inserted/updated:', s);
  } catch (err) {
    console.error('❌ Error inserting student:', err);
  }
}

addStudent();
