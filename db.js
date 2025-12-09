require('dotenv').config();
const mongoose = require('mongoose');

const uri = process.env.MONGO_URI || 'mongodb+srv://praveen:yourstrongpassword123@attendancedb.tpwmjgs.mongodb.net/?appName=AttendanceDB';

mongoose.connect(uri)
  .then(() => console.log('✅ Mongoose connected'))
  .catch(err => console.error('Mongo connect error:', err));

mongoose.connection.on('error', err => console.error('Mongoose connection error:', err));
mongoose.connection.on('disconnected', () => console.warn('Mongoose disconnected'));

process.on('SIGINT', async () => {
  await mongoose.connection.close();
  process.exit(0);
});

module.exports = mongoose;
