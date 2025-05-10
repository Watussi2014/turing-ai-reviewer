
import { PutCommand } from "@aws-sdk/lib-dynamodb";
import { docClient } from "./aws-config";
import { uploadFileToS3 } from "./s3";

export const saveProjectDescription = async (projectData) => {
  const command = new PutCommand({
    TableName: "project_descriptions_db",
    Item: {
      project_description_id: projectData.project_descriptions_id,
      project_descriptions: projectData.project_descriptions,
      project_name: projectData.project_name,
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
  try {
    // Upload files to S3 first
    const fileUploads = await Promise.all(
      uploadData.files.map(file => uploadFileToS3(file, uploadData.project_id))
    );

    // Save project data with S3 references to DynamoDB
    const command = new PutCommand({
      TableName: "projects_db",
      Item: {
        project_id: uploadData.project_id,
        project_description_id: uploadData.project_description_id,
        grade: uploadData.grade,
        files: fileUploads, // Store S3 references
        timestamp: new Date().toISOString()
      }
    });

    await docClient.send(command);
    return true;
  } catch (error) {
    console.error("Error saving to DynamoDB:", error);
    throw error;
  }
};
