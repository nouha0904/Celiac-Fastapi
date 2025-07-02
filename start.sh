#!/bin/bash
#!uvicorn main:app --host 0.0.0.0 --port 10000
#!/bin/bash
# استخدم المسار الصحيح لملف main.py
uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-10000}