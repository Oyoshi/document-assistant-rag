import type { Meta, StoryObj } from "@storybook/react";
import { FileUploader } from "./FileUploader";

const meta: Meta<typeof FileUploader> = {
  title: "Components/FileUploader",
  component: FileUploader,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
  argTypes: {
    onUploadSuccess: { action: "uploaded" },
  },
};

export default meta;
type Story = StoryObj<typeof FileUploader>;

export const Default: Story = {};
