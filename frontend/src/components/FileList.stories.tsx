import type { Meta, StoryObj } from "@storybook/react";
import { FileList } from "./FileList";

const meta: Meta<typeof FileList> = {
  title: "Components/FileList",
  component: FileList,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
  argTypes: {
    onClearFiles: { action: "cleared" },
  },
};

export default meta;
type Story = StoryObj<typeof FileList>;

export const Empty: Story = {
  args: {
    files: [],
  },
};

export const WithFiles: Story = {
  args: {
    files: [
      { filename: "document1.pdf", chunks: 5 },
      { filename: "report_2024.pdf", chunks: 12 },
      { filename: "notes.pdf", chunks: 3 },
    ],
  },
};
