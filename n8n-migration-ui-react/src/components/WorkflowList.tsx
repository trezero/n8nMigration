import React, { useState, useMemo, useEffect } from 'react';
import { FileJson, GripVertical, Trash2, UploadCloud, Search, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label'; // Placeholder
// import { Input } from '@/components/ui/input'; // Placeholder - will add if needed for search

interface WorkflowItem {
  filename: string; // Unique identifier from backend (original filename)
  displayName: string; // Name to show in UI
  file_type: 'workflow' | 'credential' | 'unknown'; // Type from backend
  // 'id' for React list keys and selection will be derived from filename
  id: string; 
}



const API_BASE_URL = 'http://localhost:5000'; // Flask server

export const WorkflowList: React.FC = () => {
  const [workflows, setWorkflows] = useState<WorkflowItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchWorkflows = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch(`${API_BASE_URL}/api/files`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        // Transform data to match WorkflowItem interface, using filename as id
        const transformedData: WorkflowItem[] = data.map((item: { filename: string; displayName: string; file_type: 'workflow' | 'credential' | 'unknown' }) => ({
          ...item,
          id: item.filename, // Use filename as the unique ID for React components
        }));
        setWorkflows(transformedData.filter(item => item.file_type === 'workflow')); // Only show workflows for now
      } catch (e) {
        console.error('Failed to fetch workflows:', e);
        setError(e instanceof Error ? e.message : String(e));
      }
      setIsLoading(false);
    };

    fetchWorkflows();
  }, []);
  const [selectedWorkflows, setSelectedWorkflows] = useState<Set<string>>(new Set());
  const [searchTerm, setSearchTerm] = useState('');

  const handleSelectWorkflow = (filename: string) => {
    setSelectedWorkflows((prev: Set<string>) => {
      const next = new Set(prev);
      if (next.has(filename)) {
        next.delete(filename);
      } else {
        next.add(filename);
      }
      return next;
    });
  };

  const handleSelectAll = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      setSelectedWorkflows(new Set(filteredWorkflows.map((wf: WorkflowItem) => wf.filename))); // Use filename for selection
    } else {
      setSelectedWorkflows(new Set());
    }
  };

  const handleImportSelected = () => {
    if (selectedWorkflows.size === 0) {
      console.log('No workflows selected for import.');
      return;
    }

    const filesToImport = Array.from(selectedWorkflows); // selectedWorkflows now stores filenames
    console.log(`Attempting to import ${filesToImport.length} workflows:`, filesToImport);

    fetch(`${API_BASE_URL}/import-workflows`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ workflow_files: filesToImport }),
    })
    .then(response => response.json())
    .then(data => {
      console.log('Import Response:', data);
      // Combine messages for the alert
      let alertMessage = `Overall Success: ${data.success}\n\nResults:\n`;
      if (data.results && Array.isArray(data.results)) {
        data.results.forEach((result: { file: string; success: boolean; message: string }) => {
          alertMessage += `- ${result.file}: ${result.success ? 'OK' : 'Failed'} (${result.message})\n`;
        });
      } else if (data.message) {
        alertMessage = data.message; // For top-level error messages
      }
      alert(alertMessage);
      // TODO: Use Toasts for better UX
      // Potentially refresh workflow list or update status here
    })
    .catch(err => {
      console.error('Import Error:', err);
      alert(`Failed to send import request: ${err.message}`);
    });
  };

  const filteredWorkflows = useMemo(() => {
    return workflows.filter((wf: WorkflowItem) => 
      wf.displayName.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [workflows, searchTerm]);

  const isAllSelected = filteredWorkflows.length > 0 && selectedWorkflows.size === filteredWorkflows.length;

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center">
          <UploadCloud className="mr-2 h-6 w-6" />
          Import Workflows
        </CardTitle>
        <CardDescription>
          Select workflow JSON files to import. You can drag and drop files here too (feature coming soon).
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="mb-4 flex items-center gap-2">
          {/* Basic search input - consider replacing with shadcn Input later */}
          <div className="relative w-full">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <input 
              type="search" 
              placeholder="Search workflows..."
              className="pl-8 w-full h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <Button variant="outline" size="icon" className="shrink-0">
            <Filter className="h-4 w-4" />
            <span className="sr-only">Filter</span>
          </Button>
        </div>

        <div className="flex items-center py-2 border-b border-t px-1">
          <Checkbox 
            id="select-all-workflows"
            checked={isAllSelected}
            onCheckedChange={(checked: boolean | 'indeterminate') => {
              // Adapt Checkbox onCheckedChange signature if it's different for shadcn
              const pseudoEvent = { target: { checked: !!checked } } as React.ChangeEvent<HTMLInputElement>; 
              handleSelectAll(pseudoEvent);
            }}
            aria-label="Select all workflows"
            className="mr-3"
          />
          <Label htmlFor="select-all-workflows" className="flex-1 text-sm font-medium">
            {isAllSelected ? 'Deselect All' : 'Select All'} ({selectedWorkflows.size} / {filteredWorkflows.length} selected)
          </Label>
          <Button variant="ghost" size="sm" disabled={selectedWorkflows.size === 0}>
            <Trash2 className="mr-2 h-4 w-4" /> Remove Selected (mock)
          </Button>
        </div>

        <ScrollArea className="h-[300px] w-full rounded-md border p-0">
          {isLoading && (
            <div className="p-4 text-center text-muted-foreground">Loading workflows...</div>
          )}
          {!isLoading && error && (
            <div className="p-4 text-center text-red-500">Error fetching workflows: {error}</div>
          )}
          {!isLoading && !error && filteredWorkflows.length === 0 && (
            <div className="p-4 text-center text-muted-foreground">
              No workflows found{searchTerm ? ` matching "${searchTerm}"` : ''}.
            </div>
          )}
          {!isLoading && !error && filteredWorkflows.map((workflow: WorkflowItem) => (
            <div key={workflow.filename} className="flex items-center p-3 border-b last:border-b-0 hover:bg-muted/50 transition-colors">
              <Checkbox 
                id={`wf-${workflow.filename}`}
                checked={selectedWorkflows.has(workflow.filename)}
                onCheckedChange={() => handleSelectWorkflow(workflow.filename)}
                aria-labelledby={`wf-label-${workflow.filename}`}
                className="mr-3"
              />
              <GripVertical className="h-5 w-5 mr-2 text-muted-foreground cursor-grab" />
              <FileJson className="h-5 w-5 mr-3 text-primary" />
              <div className="flex-1">
                <Label htmlFor={`wf-${workflow.filename}`} id={`wf-label-${workflow.filename}`} className="font-medium truncate block cursor-pointer">
                  {workflow.displayName}
                </Label>
                {/* <p className="text-xs text-muted-foreground">{workflow.size}</p> */}
              </div>
            </div>
          ))}
        </ScrollArea>
      </CardContent>
      <CardFooter className="flex justify-end">
        <Button disabled={selectedWorkflows.size === 0} onClick={handleImportSelected}>
          <UploadCloud className="mr-2 h-4 w-4" />
          Import Selected ({selectedWorkflows.size}) Workflows
        </Button>
      </CardFooter>
    </Card>
  );
};
