import { MongoClient } from "mongodb";

const connString = process.env.MONGO_DB_CONN_STRING;

if (!connString) {
  throw new Error(
    "Please define the MONGO_DB_CONN_STRING environment variable"
  );
}

let client: MongoClient;
let clientPromise: Promise<MongoClient>;

client = new MongoClient(connString);
clientPromise = client.connect();

export default clientPromise;
