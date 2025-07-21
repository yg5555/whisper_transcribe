#!/bin/bash
cd backend && PYTHONPATH=./ uvicorn app.main:app --reload &
cd frontend && npm run dev
