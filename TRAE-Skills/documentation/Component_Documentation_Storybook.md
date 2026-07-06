# Skill: Component Documentation (Storybook)

## Purpose
To create an interactive, isolated environment for developing, documenting, and testing UI components. This acts as a living style guide for developers and designers, ensuring consistency across a large application.

## When to Use
- When building a reusable UI library (e.g., buttons, inputs, cards)
- When collaborating between frontend developers and UI/UX designers
- When documenting edge cases and states (e.g., loading, error, disabled)
- To avoid "copy-pasting" components without knowing their full functionality

## Procedure

### 1. Installation
Install Storybook into an existing project (React, Vue, Angular, Svelte, etc.).

```bash
npx storybook@latest init
```

### 2. Creating a Story
Stories represent the different states of a single component.

**`Button.stories.tsx`**
```tsx
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

// 1. Meta Configuration
const meta: Meta<typeof Button> = {
  title: 'Components/Button', // Categorization in sidebar
  component: Button,
  tags: ['autodocs'], // Automatically generate documentation page
  argTypes: {
    backgroundColor: { control: 'color' }, // Add UI controls
    onClick: { action: 'clicked' }, // Log actions
  },
};

export default meta;
type Story = StoryObj<typeof Button>;

// 2. Define Primary State
export const Primary: Story = {
  args: {
    label: 'Primary Button',
    variant: 'primary',
  },
};

// 3. Define Secondary State
export const Secondary: Story = {
  args: {
    label: 'Secondary Button',
    variant: 'secondary',
  },
};

// 4. Define Large Button
export const Large: Story = {
  args: {
    size: 'large',
    label: 'Large Button',
  },
};
```

### 3. Adding Documentation (Markdown/MDX)
For more complex components, use MDX to combine Markdown and JSX for rich documentation.

**`Button.mdx`**
```markdown
import { Meta, Story, Canvas, Controls } from '@storybook/blocks';
import * as ButtonStories from './Button.stories';

<Meta of={ButtonStories} />

# Button Component

The Button is used to trigger an action or event.

## When to use
- Form submissions
- Navigation (if it looks like a button)
- Triggering modals

<Canvas of={ButtonStories.Primary} />

## Properties
<Controls />

## Examples

### Secondary
<Story of={ButtonStories.Secondary} />
```

### 4. Running Storybook
Launch the development server to view your documentation.
```bash
npm run storybook
```

## Best Practices
- **Component Isolation**: Components in Storybook should not depend on global application state (Redux, Context) if possible. Use decorators to provide mock state when necessary.
- **Autodocs**: Enable the `autodocs` tag to get a clean table of props and examples for every component with minimal effort.
- **Visual Testing**: Integrate Storybook with tools like Chromatic for automated visual regression testing of your components.
- **Organize by Category**: Use a clear hierarchy in `title` (e.g., `Atom/Button`, `Molecule/SearchForm`, `Organism/Navbar`).