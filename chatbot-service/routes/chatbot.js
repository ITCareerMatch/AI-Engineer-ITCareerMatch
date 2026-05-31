const express = require("express");
const axios = require("axios");
const { createClient } = require("@supabase/supabase-js");
const router = express.Router();

const FASTAPI_URL = process.env.FASTAPI_URL || "http://localhost:8000";
const INTERNAL_HEADERS = {
  "x-internal-request": process.env.INTERNAL_API_KEY,
};

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY,
);

// POST /api/chatbot/chat
router.post("/chat", async (req, res) => {
  try {
    const { message, history } = req.body;
    const userId = req.session?.user?.id;
    let enrichedMessage = message;

    if (userId) {
      const { data: cv } = await supabase
        .from("cv_archives")
        .select("raw_text")
        .eq("user_id", userId)
        .order("created_at", { ascending: false })
        .limit(1)
        .single();

      if (cv?.raw_text) {
        enrichedMessage = `[Konteks CV User]\n${cv.raw_text}\n\n[Pertanyaan User]\n${message}`;
      }
    }

    // headers sebagai parameter ketiga, bukan di dalam body
    const response = await axios.post(
      `${FASTAPI_URL}/chat`,
      { message: enrichedMessage, history: history || [] },
      { headers: INTERNAL_HEADERS },
    );

    res.json(response.data);
  } catch (error) {
    const status = error.response?.status || 500;
    const detail = error.response?.data?.detail || "Chatbot service error";
    res.status(status).json({ error: detail });
  }
});

// POST /api/chatbot/tts
router.post("/tts", async (req, res) => {
  try {
    const { text, voice } = req.body;

    const response = await axios.post(
      `${FASTAPI_URL}/tts`,
      { text, voice },
      { headers: INTERNAL_HEADERS, responseType: "arraybuffer" },
    );

    res.set("Content-Type", "audio/wav");
    res.send(response.data);
  } catch (error) {
    res.status(500).json({ error: "TTS error" });
  }
});

// GET /api/chatbot/voices
router.get("/voices", async (req, res) => {
  try {
    const response = await axios.get(`${FASTAPI_URL}/tts/voices`, {
      headers: INTERNAL_HEADERS,
    });
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: "Gagal ambil daftar voice" });
  }
});

// GET /api/chatbot/health
router.get("/health", async (req, res) => {
  try {
    const response = await axios.get(`${FASTAPI_URL}/health`, {
      headers: INTERNAL_HEADERS,
    });
    res.json(response.data);
  } catch (error) {
    res.status(503).json({ error: "FastAPI tidak dapat dijangkau" });
  }
});

module.exports = router;
