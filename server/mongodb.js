// MongoDB connection setup
const { MongoClient } = require('mongodb');

const uri = process.env.MONGODB_URI || 'mongodb+srv://r3m060:vR5QPM2169FWQ1K3@cluster0.h9andhm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0';
const client = new MongoClient(uri);

async function connectDB() {
  try {
    await client.connect();
    console.log('Connected to MongoDB');
    // Connect to the "users" database and return the "users_data" collection
    const db = client.db('users');
    const collection = db.collection('user_data');
    console.log('Connected to users_data collection');
    // plot the collection data
    console.log('Collection data:', await collection.find({}).toArray());
    return collection;
  } catch (err) {
    console.error('MongoDB connection error:', err);
    throw err;
  }
}

module.exports = { connectDB, client };

connectDB();
