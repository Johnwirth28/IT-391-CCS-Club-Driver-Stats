// Import required libraries
import express from "express";
import XLSX from "xlsx";
import cors from "cors";
import path from "path";
import { fileURLToPath } from "url";

// === Path setup for ES Modules ===
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// === Express app setup ===
const app = express();
app.use(cors());

// Serve static files (HTML, JS, CSS)
app.use(express.static(__dirname));

// === Port and Excel file path ===
const PORT = process.env.PORT || 3000;
const EXCEL_PATH = path.join(__dirname, "race_data.xlsx");

// === Homepage route ===
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "HTML", "driver_status_home.html"));
});

// === API route: get Excel data as JSON ===
app.get("/api/results", (req, res) => {
  try {
    const workbook = XLSX.readFile(EXCEL_PATH);     // Read Excel file
    const sheetName = workbook.SheetNames[0];       // Get first sheet
    const sheet = workbook.Sheets[sheetName];
    const data = XLSX.utils.sheet_to_json(sheet);   // Convert to JSON
    res.json(data);                                 // Send to frontend
  } catch (err) {
    console.error("❌ Error reading Excel file:", err);
    res.status(500).json({ error: "Failed to read race data" });
  }
});

// === Start the server ===
app.listen(PORT, () => {
  console.log(`✅ Server running on http://localhost:${PORT}`);
  console.log(`🌐 Live site: https://friendly-halibut-jjwxvwgwqwqrh5w79-${PORT}.app.github.dev/`);
});



