import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 5174; // Using same port as Vite previously to keep URLs working

// Disable caching for JavaScript files during development
app.use((req, res, next) => {
    if (req.url.endsWith('.js') || req.url.endsWith('.css')) {
        res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
        res.setHeader('Pragma', 'no-cache');
        res.setHeader('Expires', '0');
    }
    next();
});

// Serve static files from public directory
app.use(express.static(path.join(__dirname, 'public')));

// SPA fallback
app.use((req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index-new.html'));
});

app.listen(PORT, () => {
    console.log(`Frontend Node Server running silently on http://localhost:${PORT}`);
});
