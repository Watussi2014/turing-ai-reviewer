
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient } from "@aws-sdk/lib-dynamodb";
import { S3Client } from "@aws-sdk/client-s3";

// Initialize the DynamoDB client
const dynamoClient = new DynamoDBClient({
  region: "YOUR_AWS_REGION",
  credentials: {
    accessKeyId: "YOUR_ACCESS_KEY_ID",
    secretAccessKey: "YOUR_SECRET_ACCESS_KEY"
  }
});

// Create a DynamoDB Document client
export const docClient = DynamoDBDocumentClient.from(dynamoClient);

// Initialize the S3 client for file uploads
export const s3Client = new S3Client({
  region: "YOUR_AWS_REGION",
  credentials: {
    accessKeyId: "YOUR_ACCESS_KEY_ID",
    secretAccessKey: "YOUR_SECRET_ACCESS_KEY"
  }
});
