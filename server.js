    const express = require("express");
    const fs = require("fs");
    const cors = require("cors");
    const { exec } = require("child_process"); // Added exec import

    const app = express();
    app.use(express.json());
    app.use(cors());

    app.post("/save-config", (req, res) => {
        const jsonData = JSON.stringify(req.body, null, 4);
        fs.writeFileSync("config.json", jsonData);
        res.send({ message: "Data saved to config.json!" });
    });

    app.post("/start-applying", (req, res) => {
        exec("python main.py", (error, stdout, stderr) => {
            if (error) {
                console.error(`Error: ${error.message}`);
                return res.status(500).send({ message: "Error executing script" });
            }
            if (stderr) {
                console.error(`Stderr: ${stderr}`);
                return res.status(500).send({ message: "Script error" });
            }
            console.log(`Output: ${stdout}`);
            res.send({ message: "Application process started successfully!" });
        });
    });

    app.listen(3000, () => console.log("Server running on port 3000"));