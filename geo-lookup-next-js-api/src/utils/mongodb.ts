// utils/mongodb.ts

import { MongoClient } from 'mongodb';

const connString = process.env.MONGO_DB_CONN_STRING;

if (!connString) {
  throw new Error('Please define the MONGO_DB_CONN_STRING environment variable');
}

let client: MongoClient;
let clientPromise: Promise<MongoClient>;

if (process.env.NODE_ENV === 'development') {
  // In development mode, use a global variable to preserve the value
  // across module reloads caused by HMR (Hot Module Replacement).
  let globalWithMongo = global as typeof globalThis & {
    _mongoClientPromise?: Promise<MongoClient>;
  };

  if (!globalWithMongo._mongoClientPromise) {
    client = new MongoClient(connString);
    globalWithMongo._mongoClientPromise = client.connect();
  }
  clientPromise = globalWithMongo._mongoClientPromise!
} else {
  // In production mode, it's best to not use a global variable.
  client = new MongoClient(connString);
  clientPromise = client.connect();
}

export default clientPromise;
