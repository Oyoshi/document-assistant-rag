import { useState } from "react";
import { FileUploader } from "./components/FileUploader";
import { FileList, type UploadedFile } from "./components/FileList";
import { ChatInterface } from "./components/ChatInterface";
import { Toaster } from "@/components/ui/sonner";
import { logger } from "@/lib/logger";

function App() {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);

  const handleUploadSuccess = (filename: string, chunks: number) => {
    setUploadedFiles((prev) => [...prev, { filename, chunks }]);
  };

  const handleClearFiles = async () => {
    try {
      const response = await fetch("/documents", { method: "DELETE" });
      if (response.ok) {
        setUploadedFiles([]);
      } else {
        logger.error("Failed to delete documents");
      }
    } catch (error) {
        logger.error("Error clearing documents:", error instanceof Error ? error.message : "Unknown error");
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="mx-auto py-4 px-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
                <h1 className="text-2xl font-bold tracking-tight">RAG Document Assistant</h1>
            </div>
        </div>
      </header>

      <main className="px-12 flex justify-center items-center">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-4 flex flex-col gap-6 h-full overflow-hidden">
            <div className="flex-shrink-0">
                <FileUploader onUploadSuccess={handleUploadSuccess} />
            </div>

            <div className="flex-1 overflow-hidden">
                <FileList files={uploadedFiles} onClearFiles={handleClearFiles} />
            </div>
          </div>
          <div className="lg:col-span-8 h-full flex flex-col">
            <ChatInterface />
          </div>
        </div>
      </main>
      <Toaster />
    </div>
  );
}

export default App;
