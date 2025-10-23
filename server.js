const express = require("express");
const fetch = require("node-fetch");
const app = express();
const PORT = 3000;

// Serve static files (if not already added)
app.use(express.static("HTML"));

// Load event data (rename your .txt file to .json if needed)
const eventData = require("./ExampleEventPageScraperOutput.json");

// Route 1: Get race results
app.get("/api/races", async (req, res) => {
  const races = [];

  for (const sessionDate in eventData.sessions) {
    const session = eventData.sessions[sessionDate][0]; // raw session
    const date = session.data.date;
    const entries = session.data.entries;

    for (const entry of entries) {
      races.push({
        date,
        driver: entry.driver_name,
        car: entry.car_model,
        raw_time: entry.raw_time,
        class: entry.class_abrv,
      });
    }
  }

  res.json(races);
});

// Route 2: Get weather for a date
app.get("/api/weather/:date", async (req, res) => {
  const date = new Date(req.params.date);
  const timestamp = Math.floor(date.getTime() / 1000);
  const lat = 40.1164; // Champaign, IL
  const lon = -88.2434;
  const apiKey = "4fe622efc66879c6e0c78c0b4e647fe3";

  const url = `https://api.openweathermap.org/data/3.0/onecall/timemachine?lat=${lat}&lon=${lon}&dt=${timestamp}&appid=${apiKey}&units=imperial`;

  try {
    const response = await fetch(url);
    const data = await response.json();
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: "Weather fetch failed", details: err.message });
  }
});

app.listen(PORT, () => console.log(`✅ Server running on http://localhost:${PORT}`));


