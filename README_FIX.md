# VisionQuest core module repair

The deployed app imports `core.cloud_db` and `core.cloud_vision`. This folder must be placed in the GitHub repository ROOT beside `app.py` and `requirements.txt`.

Expected repository layout:

```
app.py
requirements.txt
core/
  __init__.py
  cloud_db.py
  cloud_vision.py
```

Copy the `core` folder into the repository root, commit, and push the change. Do not upload this ZIP as a ZIP file to GitHub; extract it first.
