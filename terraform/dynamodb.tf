resource "aws_dynamodb_table" "project_descriptions" {
  name           = "ProjectDescriptions"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "project_description_id"

  attribute {
    name = "project_description_id"
    type = "S"
  }
}

resource "aws_dynamodb_table" "projects" {
  name           = "Projects"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "project_id"

  attribute {
    name = "project_id"
    type = "S"
  }
}