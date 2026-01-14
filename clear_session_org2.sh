#!/bin/bash
curl -X POST http://localhost:3000/api/clear-corrupted-session \
  -H "x-api-key: opticaapp_2026_whatsapp_baileys_secret_key_12345" \
  -H "Content-Type: application/json" \
  -d '{"organization_id": "2"}'
