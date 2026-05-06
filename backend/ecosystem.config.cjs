// PM2 ecosystem for FinderOS / SoarB2B (DigitalOcean Ubuntu)
// Required secrets: set on server with export, then: pm2 restart soarb2b --update-env
// See docs or checklist for: DATABASE_URL, JWT_SECRET, SOARB2B_API_KEYS, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
module.exports = {
  apps: [
    {
      name: "soarb2b",
      cwd: "/var/www/finder_os/backend",
      script: "/var/www/finder_os/venv/bin/python3",
      args: "-m uvicorn src.app:app --host 0.0.0.0 --port 8000",
      interpreter: "none",
      autorestart: true,
      max_restarts: 10,
      min_uptime: "5s",
      max_memory_restart: "800M",
      error_file: "./logs/soarb2b-error.log",
      out_file: "./logs/soarb2b-out.log",
      merge_logs: true,
      env: {
        ENV: "production",
        BASE_URL: "https://soarb2b.com",
        FINDEROS_VERSION: "1.0.0",
        FINDEROS_CORS_ORIGINS: "https://soarb2b.com,https://www.soarb2b.com",
        DATABASE_URL: process.env.DATABASE_URL,
        JWT_SECRET: process.env.JWT_SECRET,
        SOARB2B_API_KEYS: process.env.SOARB2B_API_KEYS,
        GOOGLE_CLIENT_ID: process.env.GOOGLE_CLIENT_ID,
        GOOGLE_CLIENT_SECRET: process.env.GOOGLE_CLIENT_SECRET,
      },
    },
  ],
};
