
import React, { useState } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { useToast } from "@/components/ui/use-toast";
import { saveProjectDescription } from "@/lib/dynamodb";

const ProjectForm = () => {
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    project_descriptions_id: "",
    project_descriptions: "",
    project_name: ""
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.project_descriptions_id.trim() || 
        !formData.project_descriptions.trim() || 
        !formData.project_name.trim()) {
      toast({
        title: "Missing Fields",
        description: "Please fill in all required fields",
        variant: "destructive",
      });
      return;
    }

    setIsSubmitting(true);
    
    try {
      await saveProjectDescription({
        ...formData,
        created_at: new Date().toISOString()
      });
      
      toast({
        title: "Project created successfully",
        description: "Your project has been saved to DynamoDB",
      });
      
      // Reset form
      setFormData({
        project_descriptions_id: "",
        project_descriptions: "",
        project_name: ""
      });
    } catch (error) {
      toast({
        title: "Error",
        description: error.message,
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

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card className="w-full max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-center">
            Create New Project
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="project_descriptions_id">
                Project Descriptions ID <span className="text-destructive">*</span>
              </Label>
              <Input
                id="project_descriptions_id"
                name="project_descriptions_id"
                value={formData.project_descriptions_id}
                onChange={handleChange}
                placeholder="Enter project descriptions ID"
                required
                className="border-primary/20 focus:border-primary"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="project_descriptions">
                Project Descriptions <span className="text-destructive">*</span>
              </Label>
              <Input
                id="project_descriptions"
                name="project_descriptions"
                value={formData.project_descriptions}
                onChange={handleChange}
                placeholder="Enter project descriptions"
                required
                className="border-primary/20 focus:border-primary"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="project_name">
                Project Name <span className="text-destructive">*</span>
              </Label>
              <Input
                id="project_name"
                name="project_name"
                value={formData.project_name}
                onChange={handleChange}
                placeholder="Enter project name"
                required
                className="border-primary/20 focus:border-primary"
              />
            </div>
          </form>
        </CardContent>
        <CardFooter>
          <Button 
            onClick={handleSubmit}
            className="w-full bg-primary hover:bg-primary/90"
            disabled={isSubmitting}
          >
            {isSubmitting ? "Creating Project..." : "Create Project"}
          </Button>
        </CardFooter>
      </Card>
    </motion.div>
  );
};

export default ProjectForm;
