const express = require('express');
const fs = require('fs');
const cors = require('cors');
const { spawn } = require('child_process');
const path = require('path');

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());

// Serve web.html at the root URL
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'GUI_Foundit.html'));
});

// Save config.json
app.post('/save-config', (req, res) => {
  const config = req.body;

  fs.writeFile('config_Foundit.json', JSON.stringify(config, null, 2), (err) => {
    if (err) {
      console.error('Error saving config:', err);
      return res.status(500).json({ message: 'Failed to save config file.' });
    }
    console.log('Config saved successfully.');
    res.json({ message: 'Config saved successfully!' });
  });
});

// Run main.py
app.post('/start-applying', (req, res) => {
  const pythonProcess = spawn('python', ['main_Foundit.py']);

  let output = '';
  let errorOutput = '';

  pythonProcess.stdout.on('data', (data) => {
    output += data.toString();
  });

  pythonProcess.stderr.on('data', (data) => {
    errorOutput += data.toString();
  });

  pythonProcess.on('close', (code) => {
    if (code === 0) {
      res.json({ message: output });
    } else {
      res.status(500).json({ message: `Error: ${errorOutput}` });
    }
  });
});

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
