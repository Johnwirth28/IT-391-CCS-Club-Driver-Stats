//is a test to see if it works

// server.js
const express = require("express");
const bodyParser = require("body-parser");
const mysql = require("mysql2");
const bcrypt = require("bcrypt");

const app = express();
app.use(bodyParser.urlencoded({ extended: true }));

// connect to DB
const db = mysql.createConnection({
  host: "localhost",
  user: "root",
  password: "yourpassword",
  database: "driver_stats"
});

// handle login
app.post("/login", (req, res) => {
  const { username, password } = req.body;

  db.query("SELECT * FROM users WHERE username = ?", [username], (err, results) => {
    if (err) throw err;

    if (results.length === 0) {
      return res.send("Username not found ❌");
    }

    const user = results[0];
    bcrypt.compare(password, user.password, (err, match) => {
      if (match) {
        res.send("✅ Login successful!");
      } else {
        res.send("❌ Incorrect password");
      }
    });
  });
});

app.listen(3000, () => console.log("Server running on port 3000"));