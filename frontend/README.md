# Ovi Frontend - Modern Web Interface

A beautiful, responsive web interface for Ovi video generation, inspired by Open WebUI.

## Features

- 🎨 Modern, dark-themed UI with smooth animations
- 📱 Responsive design for mobile and desktop
- 🎬 Real-time queue management
- 🔄 Live progress tracking via WebSockets
- 📝 Prompt templates for quick start
- ⚙️ Advanced configuration options
- 🎯 Support for T2V and I2V modes

## Getting Started

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

Visit `http://localhost:3000` to see the interface.

### Production Build

```bash
npm run build
npm start
```

## Architecture

- **Next.js 14**: React framework with server-side rendering
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Animation library
- **Socket.IO**: Real-time communication
- **TypeScript**: Type-safe development

## Components

- `Header`: Navigation and branding
- `VideoGenerator`: Main generation interface
- `QueuePanel`: Live queue management
- `PromptTemplates`: Pre-made prompt templates

## Configuration

The frontend connects to the backend API at `http://localhost:8000`. Update this in:
- `next.config.js` for API rewrites
- `queueContext.tsx` for WebSocket connection

## Customization

### Theme Colors

Edit `tailwind.config.js` to customize the color scheme:

```js
theme: {
  extend: {
    colors: {
      primary: { /* your colors */ }
    }
  }
}
```

### Templates

Add or modify prompt templates in `components/PromptTemplates.tsx`.

## Integration with Backend

The frontend expects the backend to provide:

1. **REST API** endpoints:
   - `POST /api/generate` - Submit generation job
   - `GET /api/jobs` - Get all jobs
   - `GET /api/jobs/:id` - Get specific job
   - `DELETE /api/jobs/:id` - Cancel job

2. **WebSocket** events:
   - `submit_job` - Submit new job
   - `cancel_job` - Cancel job
   - `job_update` - Receive job status updates

## License

Same as parent Ovi project.
