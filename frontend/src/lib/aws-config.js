
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient } from "@aws-sdk/lib-dynamodb";
import { S3Client } from "@aws-sdk/client-s3";


const credentials = {
  accessKeyId: import.meta.env.VITE_AWS_ACCESS_KEY_ID,
  secretAccessKey: import.meta.env.VITE_AWS_SECRET_ACCESS_KEY
};

const region = import.meta.env.VITE_AWS_REGION;

// Initialize the DynamoDB client
const dynamoClient = new DynamoDBClient({
  region,
  credentials
});

// Create a DynamoDB Document client
export const docClient = DynamoDBDocumentClient.from(dynamoClient);

// Initialize the S3 client for file uploads
export const s3Client = new S3Client({
  region,
  credentials
});
