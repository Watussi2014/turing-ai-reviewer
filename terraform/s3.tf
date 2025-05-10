resource "aws_s3_bucket" "project_files" {
  bucket        = "turing-hackathon-student-project-files"
  force_destroy = true
}

resource "aws_s3_bucket_cors_configuration" "student_project_files_cors" {
  bucket = aws_s3_bucket.project_files.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST", "HEAD"]
    allowed_origins = [
      "http://turing-hackathon-frontend.s3-website.eu-west-3.amazonaws.com"
    ]
    expose_headers = ["ETag"]
    max_age_seconds = 3000
  }
}

resource "aws_s3_bucket" "frontend" {
  bucket        = "turing-hackathon-frontend" 
  force_destroy = true 

  tags = {
    Name        = "FrontendHosting"
    Environment = "dev"
  }
}

resource "aws_s3_bucket_website_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.bucket

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}

resource "aws_s3_bucket_policy" "frontend_policy" {
  bucket = aws_s3_bucket.frontend.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid       = "PublicReadGetObject",
        Effect    = "Allow",
        Principal = "*",
        Action    = "s3:GetObject",
        Resource  = "${aws_s3_bucket.frontend.arn}/*"
      },
      {
      Sid = "AllowPublicRead",
      Effect = "Allow",
      Principal =  "*",
      Action = "s3:GetObject",
      Resource = "arn:aws:s3:::turing-hackathon-frontend/*"
    }
    ]
  })
}