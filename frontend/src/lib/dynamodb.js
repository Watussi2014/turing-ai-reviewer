
import { PutCommand } from "@aws-sdk/lib-dynamodb";
import { docClient } from "./aws-config";

export const saveProjectDescription = async (projectData) => {
  const command = new PutCommand({
    TableName: "project_descriptions_db",
    Item: {
      ...projectData,
      timestamp: new Date().toISOString()
    }
  });

  try {
    await docClient.send(command);
    return true;
  } catch (error) {
    console.error("Error saving to DynamoDB:", error);
    throw error;
  }
};

export const saveProjectUpload = async (uploadData) => {
  const command = new PutCommand({
    TableName: "projects_db",
    Item: {
      ...uploadData,
      timestamp: new Date().toISOString()
    }
  });

  try {
    await docClient.send(command);
    return true;
  } catch (error) {
    console.error("Error saving upload to DynamoDB:", error);
    throw error;
  }
};
