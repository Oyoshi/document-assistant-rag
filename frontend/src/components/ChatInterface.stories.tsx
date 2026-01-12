import type { Meta, StoryObj } from "@storybook/react";
import { ChatInterface } from "./ChatInterface";

const meta: Meta<typeof ChatInterface> = {
  title: "Components/ChatInterface",
  component: ChatInterface,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
};

export default meta;
type Story = StoryObj<typeof ChatInterface>;

export const Default: Story = {};
