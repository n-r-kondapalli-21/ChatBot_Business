# Web UI Module

A simple, beautiful web interface for the FAQ Chatbot API.

## Features

- Clean, modern chat interface
- Real-time connection status
- Clickable FAQ list for quick questions
- Similarity score display
- Responsive design (works on mobile)
- No backend changes required

## How to Use

### Prerequisites

1. Make sure the API server is running:
```bash
cd faq_chatbot
.venv/Scripts/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

2. In a new terminal, start the web UI:

**Windows:**
```bash
cd faq_chatbot/web_ui
start.bat
```

**Or:**
```bash
cd faq_chatbot/web_ui
python serve.py
```

**Linux/Mac:**
```bash
cd faq_chatbot/web_ui
chmod +x start.sh
./start.sh
```

3. Open your browser to http://localhost:3000

## File Structure

```
web_ui/
├── index.html      # Main HTML structure
├── styles.css      # Styling and animations
├── app.js          # JavaScript logic and API calls
├── serve.py        # Simple HTTP server
└── README.md       # This file
```

## How It Works

The web UI is a completely separate module that:

1. **Serves static files** - Uses Python's built-in HTTP server
2. **Communicates with API** - Makes fetch requests to the backend
3. **No backend changes** - Works with existing API endpoints

### API Endpoints Used

- `GET /health` - Check connection status
- `GET /faqs` - Load available FAQs
- `POST /chat` - Send questions and get answers

## Customization

### Change API URL

Edit `app.js` and change:
```javascript
const API_BASE_URL = 'http://127.0.0.1:8000';
```

### Change Port

Edit `serve.py` and change:
```python
PORT = 8080
```

### Styling

Edit `styles.css` to customize colors, fonts, and layout.

## Features Explained

### Chat Interface
- Type questions in the input field
- Press Enter or click Send to submit
- See both user and bot messages
- Similarity scores shown for matched answers

### FAQ List
- Click any FAQ to ask that question
- Shows category for each FAQ
- Hover effects for better UX

### Status Bar
- Shows connection status to API
- Displays number of loaded FAQs
- Color-coded indicator (green = connected, red = disconnected)

## Browser Compatibility

Works in all modern browsers:
- Chrome/Edge
- Firefox
- Safari
- Opera

## Security Notes

- This is a simple HTTP server for development
- For production, use a proper web server (nginx, Apache)
- Currently connects to 127.0.0.1 (localhost only)
- No authentication (add if needed for production)

## Troubleshooting

### "Disconnected" status
- Make sure the API server is running on port 8000
- Check the API URL in `app.js`

### Styles not loading
- Clear browser cache
- Check that `styles.css` is in the same directory as `index.html`

### Questions not sending
- Check browser console for errors (F12)
- Verify API server is running
- Check CORS settings in the API

## Future Enhancements

- Add dark mode toggle
- Save chat history
- Export conversation
- Add user authentication
- Support multiple languages
- Add voice input
- Chat history sidebar
