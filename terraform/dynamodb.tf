resource "aws_dynamodb_table" "project_descriptions" {
  name           = "project_descriptions_db"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "project_description_id"

  attribute {
    name = "project_description_id"
    type = "S"
  }
}

resource "aws_dynamodb_table" "projects" {
  name           = "projects_db"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "project_id"

  attribute {
    name = "project_id"
    type = "S"
  }

  attribute {
    name = "project_description_id"
    type = "S"
  }

  global_secondary_index {
    name               = "project_descriptions_index"
    hash_key           = "project_description_id"
    projection_type    = "ALL"
  }
}