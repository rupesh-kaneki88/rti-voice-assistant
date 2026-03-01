# RTI Voice Assistant - Frontend

Accessible voice-first interface for filing RTI applications.

## Quick Start

1. **Install dependencies:**
```bash
npm install
```

2. **Start development server:**
```bash
npm run dev
```

3. **Open browser:**
http://localhost:3000

## Features

✅ Voice recording and transcription
✅ Text-to-speech feedback
✅ RTI form with auto-save
✅ Multi-language support (English, Hindi, Kannada)
✅ Accessibility-first design
✅ Screen reader compatible
✅ Keyboard navigation

## Accessibility Features

- ARIA labels and roles
- Keyboard navigation
- Screen reader announcements
- High contrast mode support
- Reduced motion support
- Focus indicators

## Testing

Make sure the backend is running on http://localhost:8000

Then test:
1. Select language
2. Click "Start Recording" and speak
3. Fill RTI form
4. Generate application

## Build for Production

```bash
npm run build
npm start
```

## Environment Variables

Create `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production, update to your deployed backend URL.
