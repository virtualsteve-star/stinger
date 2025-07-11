# Stinger Browser Extension Example

This example demonstrates how to integrate Stinger guardrails into a browser extension for real-time content protection.

## Features

- Real-time content checking as users type
- Visual indicators for content status (allow/warn/block)
- Form submission blocking for prohibited content
- Status indicator showing API connectivity
- Detailed guardrail information popup

## Setup

1. Start the Stinger API server:
   ```bash
   stinger-api --detached
   ```

2. Load the extension in Chrome:
   - Open `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select this directory

3. The extension will automatically monitor all text inputs and textareas on web pages.

## How It Works

### Content Monitoring
The extension monitors all text inputs and textareas, checking content after a 500ms debounce period to avoid excessive API calls.

### Visual Indicators
- **Green dot**: Content is allowed
- **Yellow dot**: Content has warnings
- **Red dot**: Content would be blocked

### Form Protection
When a form is submitted, the extension checks all inputs. If any content would be blocked, the submission is prevented and a warning is shown.

### Status Indicator
A floating status indicator in the bottom-right shows:
- **Green "Active"**: API is connected and working
- **Red "Offline"**: API is unreachable

Click the indicator to see detailed guardrail information.

## Customization

### Change Preset
Edit `content.js` and modify the `PRESET` constant:
```javascript
const PRESET = 'financial'; // Options: basic, customer_service, medical, etc.
```

### Adjust API URL
If running the API on a different host/port:
```javascript
const STINGER_API_URL = 'http://localhost:8080';
```

### Modify Visual Styling
The extension uses inline styles for simplicity. Modify the `cssText` properties in `content.js` to customize appearance.

## Security Notes

- This example connects to a local API server
- For production, use HTTPS and proper authentication
- Consider implementing rate limiting
- Validate all inputs client-side as well

## Files

- `manifest.json` - Chrome extension manifest
- `content.js` - Main content script with Stinger integration
- `README.md` - This documentation

## Next Steps

1. Add a popup UI for configuration
2. Implement background service worker for better performance
3. Add options page for user preferences
4. Support for multiple presets per site
5. Integration with specific chat platforms