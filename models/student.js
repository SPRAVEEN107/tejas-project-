// models/student.js
const mongoose = require('mongoose');
const Counter = require('./counter');

const studentSchema = new mongoose.Schema({
  name: { type: String, required: true },
  rollNo: { type: String, unique: true }, // auto-generated
  email: { type: String },
  face_encoding: { type: [Number] }
}, { timestamps: true });

studentSchema.pre('save', async function (next) {
  if (!this.isNew) return next();       // only generate for new docs
  if (this.rollNo) return next();       // if rollNo already set, skip

  // 👉 Check if students collection is empty
  const count = await mongoose.model('Student').countDocuments();

  if (count === 0) {
    // reset counter if DB is empty
    await Counter.findByIdAndUpdate(
      { _id: 'rollNo' },
      { seq: 0 },      // reset to 0
      { upsert: true }
    );
  }

  // normal increment
  const counter = await Counter.findByIdAndUpdate(
    { _id: 'rollNo' },
    { $inc: { seq: 1 } },
    { new: true, upsert: true }
  );

  this.rollNo = `${String(counter.seq).padStart(2, '0')}`;
  next();
});

module.exports = mongoose.model('Student', studentSchema);
