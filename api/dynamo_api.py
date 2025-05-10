import boto3
from botocore.exceptions import ClientError

class DynamoDBAPI:
    def __init__(self, table_name: str):
        # Initialize DynamoDB resource and the table
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(table_name)
        self.bucket_name = "turing-hackathon-student-project-files"

    def fetch_projects(self, description_id: str) -> list[dict]:
        """Fetch all projects matching the given description ID."""
        try:
            response = self.table.scan(
                FilterExpression="project_description_id = :desc_id",
                ExpressionAttributeValues={":desc_id": description_id}
            )
            return response.get("Items", [])
        except ClientError as e:
            raise RuntimeError(f"Error fetching projects by description ID: {e.response['Error']['Message']}") from e
    
    def fetch_file_path(self, description_id: str) -> None:
        """Fetch all projects file paths matching the given description ID."""
        path_list = []
        data_dict = self.fetch_projects(description_id)
        for files in data_dict:
            for file in files["files"]:
                path_list.append({"fileName": file["fileName"], "s3Key": file["s3Key"]})
        return path_list
            
    def download_project_files_from_s3(self, description_id: str) -> dict:
        """Download all project files matching the given description ID from S3.
        
        Args:
            description_id: The project description ID to match
        
        Returns:
            A dictionary mapping file names to their contents. If an error occurs
            while reading a file, the value will be a string with an error message.
        """
        
        s3_paths = self.fetch_file_path(description_id)
        s3 = boto3.client("s3")
        contents = {}
        for paths in s3_paths:
            path = paths["s3Key"]
            file_name = paths["fileName"]
            try:
                obj = s3.get_object(Bucket=self.bucket_name, Key=path)
                contents[file_name] = obj["Body"].read().decode("utf-8")
            except Exception as e:
                contents[path] = f"[Error reading file: {str(e)}]"
        return contents

    def get_descriptions(self, description_id: str) -> str:
        """Fetch the project description matching the given description ID.

        Args:
            description_id: The project description ID to match

        Returns:
            The project description matching the given description ID.
            If no projects match, returns "[No description found]".
        """
        try:
                response = self.table.scan(
                FilterExpression="project_description_id = :desc_id",
                ExpressionAttributeValues={":desc_id": description_id}
                )
                items = response.get("Items", [])

                if items:
                    return items[0].get("project_descriptions", "[No description found]")
                else:
                    raise RuntimeError(f"No projects found with description ID: {description_id}")
                
        except ClientError as e:
                raise RuntimeError(f"Error fetching projects by description ID: {e.response['Error']['Message']}") from e
