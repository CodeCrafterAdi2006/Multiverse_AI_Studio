# Skill: README Best Practices

## Purpose
To create a high-quality `README.md` that serves as the entry point for a project. A great README explains what the project does, how to get it running, and how to contribute, significantly reducing onboarding time for new developers and stakeholders.

## When to Use
- When creating a new repository or cleaning up an existing one
- When a project's setup process changes
- To improve the discoverability and usability of a tool or library
- As part of the documentation for a professional portfolio project

## Procedure

### 1. The Essential Sections
A professional README should follow a logical order:

1. **Title & Short Description**: What is this? (Include a logo or badges if applicable).
2. **Key Features**: Why should I use this? (Bullet points).
3. **Demo/Screenshots**: Show it in action.
4. **Getting Started**:
    - **Prerequisites**: (e.g., Node.js >= 18, Docker).
    - **Installation**: Step-by-step commands.
5. **Usage**: Code examples or CLI commands.
6. **Configuration**: Environment variables or config files.
7. **Architecture (Optional)**: Brief overview or diagram.
8. **Contributing**: Link to `CONTRIBUTING.md`.
9. **License**: Name of the license.

### 2. Format Example

```markdown
# 🚀 SuperApp

A modern task manager built with React and Node.js.

## ✨ Features
- **Real-time Sync**: Tasks stay in sync across devices.
- **Offline Support**: Work without an internet connection.
- **AI Priority**: Automatically categorizes tasks based on urgency.

## 🛠️ Getting Started

### Prerequisites
- Node.js v18.0.0+
- PostgreSQL v14+

### Installation
```bash
git clone https://github.com/user/superapp.git
npm install
cp .env.example .env
npm run dev
```

## 📖 Usage
Check out our [Documentation Site](https://docs.superapp.com) for advanced usage guides.
```

### 3. Writing Tips
- **Be Concise**: Developers scan READMEs. Use bold text, lists, and code blocks.
- **Use Badges**: Use [Shields.io](https://shields.io/) to show build status, test coverage, and version.
- **Relative Links**: Use relative links for files within the repo (e.g., `[Changelog](./CHANGELOG.md)`) so they work in GitHub's web interface.
- **Table of Contents**: If the README is long, add a TOC at the top.

## Best Practices
- **Assume Nothing**: Don't assume the user has your specific global tools installed. Include commands like `npx` or `brew install`.
- **Keep it Updated**: A README with broken installation commands is a major red flag.
- **Visuals Matter**: A single GIF of the app in action is worth 10 paragraphs of description.
- **Professional Tone**: Use clear, inclusive language. Avoid "just" or "simply" (e.g., instead of "Simply run this", use "Run this").
- **Link to Support**: Tell users where to go if they find a bug (GitHub Issues, Slack, etc.).