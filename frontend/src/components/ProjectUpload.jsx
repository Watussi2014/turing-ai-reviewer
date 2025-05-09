
import React, { useState } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { useToast } from "@/components/ui/use-toast";
import FileUploader from "@/components/FileUploader";
import { saveProjectUpload } from "@/lib/dynamodb";

const ProjectUpload = () => {
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    project_id: "",
    project_description_id: "",
    grade: ""
  });
  const [files, setFiles] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.project_id.trim() || 
        !formData.project_description_id.trim() || 
        !formData.grade) {
      toast({
        title: "Missing Fields",
        description: "Please fill in all required fields",
        variant: "destructive",
      });
      return;
    }

    if (files.length === 0) {
      toast({
        title: "No Files Selected",
        description: "Please select at least one file to upload",
        variant: "destructive",
      });
      return;
    }

    setIsSubmitting(true);

    try {
      await saveProjectUpload({
        ...formData,
        files: files.map(file => ({
          name: file.name,
          size: file.size,
          type: file.type
        })),
        created_at: new Date().toISOString()
      });
      
      toast({
        title: "Success!",
        description: "Your project and files have been uploaded to DynamoDB",
      });
      
      // Reset form
      setFormData({
        project_id: "",
        project_description_id: "",
        grade: ""
      });
      setFiles([]);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to upload project to DynamoDB",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFileSend = (uploadedFiles) => {
    setFiles(uploadedFiles);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-8"
    >
      <Card className="w-full max-w-3xl mx-auto">
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-center">
            Upload Project Files
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="project_id">
                Project ID <span className="text-destructive">*</span>
              </Label>
              <Input
                id="project_id"
                name="project_id"
                value={formData.project_id}
                onChange={handleChange}
                placeholder="Enter project ID"
                required
                className="border-primary/20 focus:border-primary"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="project_description_id">
                Project Description ID <span className="text-destructive">*</span>
              </Label>
              <Input
                id="project_description_id"
                name="project_description_id"
                value={formData.project_description_id}
                onChange={handleChange}
                placeholder="Enter project description ID"
                required
                className="border-primary/20 focus:border-primary"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="grade">
                Grade <span className="text-destructive">*</span>
              </Label>
              <Input
                id="grade"
                name="grade"
                type="number"
                min="0"
                max="100"
                value={formData.grade}
                onChange={handleChange}
                placeholder="Enter grade (0-100)"
                required
                className="border-primary/20 focus:border-primary"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label>
              Project Files <span className="text-destructive">*</span>
            </Label>
            <FileUploader onFileSend={handleFileSend} />
          </div>
        </CardContent>
        <CardFooter>
          <Button 
            onClick={handleSubmit}
            className="w-full bg-primary hover:bg-primary/90"
            size="lg"
            disabled={isSubmitting}
          >
            {isSubmitting ? "Submitting..." : "Submit Project and Files"}
          </Button>
        </CardFooter>
      </Card>
    </motion.div>
  );
};

export default ProjectUpload;
