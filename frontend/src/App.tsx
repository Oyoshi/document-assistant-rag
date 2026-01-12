import { useState } from "react";
import { FileUploader } from "./components/FileUploader";
import { FileList, type UploadedFile } from "./components/FileList";
import { ChatInterface } from "./components/ChatInterface";
import { Toaster } from "@/components/ui/sonner";
import { logger } from "@/lib/logger";
import { ThemeProvider } from "@/components/ThemeProvider";
import { ModeToggler } from "@/components/ModeToggler";

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
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme" attribute="class">
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="mx-auto py-4 px-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
                <h1 className="text-2xl font-bold tracking-tight">RAG Document Assistant</h1>
            </div>
            <ModeToggler />
        </div>
      </header>

      <main className="w-full min-h-screen p-4 md:p-6">
  <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 w-full h-full">
    <div className="lg:col-span-4 flex flex-col gap-6">
      <div className="flex-shrink-0">
        <FileUploader onUploadSuccess={handleUploadSuccess} />
      </div>

      <div className="flex-1 overflow-hidden">
        <FileList files={uploadedFiles} onClearFiles={handleClearFiles} />
      </div>
    </div>
    <div className="lg:col-span-8 flex flex-col h-full min-h-[500px]">
      <ChatInterface />
    </div>

  </div>
</main>
      <Toaster />
    </div>
    </ThemeProvider>
  );
}

export default App;
