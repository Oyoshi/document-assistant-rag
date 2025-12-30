import { FileText, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

export interface UploadedFile {
  filename: string;
  chunks: number;
}

interface FileListProps {
  files: UploadedFile[];
  onClearFiles: () => void;
}

export function FileList({ files, onClearFiles }: FileListProps) {
  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle>Uploaded Files</CardTitle>
          {files.length > 0 && (
            <Button variant="destructive" size="sm" onClick={onClearFiles}>
              <Trash2 className="h-4 w-4 mr-2" />
              Clear All
            </Button>
          )}
        </div>
      </CardHeader>
      <Separator />
      <CardContent className="flex-1 overflow-auto p-0">
        {files.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-muted-foreground">
            <FileText className="h-12 w-12 mb-2 opacity-20" />
            <p className="text-sm">No files uploaded yet.</p>
          </div>
        ) : (
          <ul className="divide-y">
            {files.map((file, index) => (
              <li key={index} className="flex items-center justify-between p-4 hover:bg-muted/50 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="bg-primary/10 p-2 rounded-md">
                    <FileText className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <p className="text-sm font-medium truncate max-w-[180px]" title={file.filename}>
                      {file.filename}
                    </p>
                    <p className="text-xs text-muted-foreground">{file.chunks} chunks</p>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
