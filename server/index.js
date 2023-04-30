const express = require("express");
const cors = require("cors");
const multer = require("multer");
const moment = require("moment");
const knex = require("knex")({
  client: "pg",
  connection: {
    host: "45.12.238.37",
    port: 5432,
    user: "postgres",
    password: "changeme",
    database: "postgres",
  },
});

const storage = multer.diskStorage({
  destination(req, file, cb) {
    cb(null, "uploads/");
  },
  filename(req, file, cb) {
    cb(null, `${file.originalname}`);
  },
});

const upload = multer({ storage });

const app = express();

app.use(cors());

app.post("/", upload.single("photo"), (req, res) => {
  if (!req.file) {
    res.status(400).send("No file uploaded.");
  }
  const fileName = req.file.filename;
  const fileUrl = `${req.protocol}://${req.get("host")}/uploads/${fileName}`;
  res.json(fileUrl);
});

app.get("/", async (req, res) => {
  if (req.query.table && req.query.find) {
    const r = await knex(req.query.table).whereLike("event_name", `%${req.q}`);
    res.json(r);
  }
  if (req.query.table) {
    const r = await knex(req.query.table).select();
    res.json(r);
  }
});

app.listen(3000);
