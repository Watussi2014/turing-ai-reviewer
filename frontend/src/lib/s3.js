
import { PutObjectCommand } from "@aws-sdk/client-s3";
import { s3Client } from "./aws-config";

const S3_BUCKET_NAME = "turing-hackathon-student-project-files";

export const uploadFileToS3 = async (file, projectId) => {
  const fileExtension = file.name.split('.').pop();
  const uniqueFileName = `${projectId}/${Date.now()}-${Math.random().toString(36).substring(7)}.${fileExtension}`;

  try {
    // Read the file as an ArrayBuffer
    const fileArrayBuffer = await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsArrayBuffer(file);
    });

    const command = new PutObjectCommand({
      Bucket: S3_BUCKET_NAME,
      Key: uniqueFileName,
      Body: new Uint8Array(fileArrayBuffer),
      ContentType: file.type,
    });

    await s3Client.send(command);
    return {
      fileName: file.name,
      s3Key: uniqueFileName,
      size: file.size,
      type: file.type
    };
  } catch (error) {
    console.error("Error uploading to S3:", error);
    throw error;
  }
};
