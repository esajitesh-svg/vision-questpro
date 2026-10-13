# Smriti AI / VisionQuest — Cloud Edition

This is a **cloud-deployment edition** of the VisionQuest demo. Unlike the local Ollama build, it runs the small public vision model `HuggingFaceTB/SmolVLM-256M-Instruct` on the hosting server using Transformers. Users can open a hosted HTTPS URL from a phone, tablet, or computer.

## Important differences from the local edition

- Use **browser camera capture** (`st.camera_input`) or image upload. A cloud server cannot use `cv2.VideoCapture(0)` to access a visitor's webcam.
- This edition supports one still image per analysis. It does not provide continuous live video monitoring.
- The demo vault is a single shared SQLite database on the app host and is protected by one app password. Anyone with that password can see and export the same demo records.
- The default Streamlit Community Cloud filesystem should not be treated as durable storage. A restart/redeploy can cause database loss. Do not store real medical or sensitive personal information. Use fictional demo records only.
- This is a prototype, not a medical device or validated dementia-support system.

## Deploy to a public HTTPS URL (Streamlit Community Cloud)

### 1. Create a repository

1. Download and extract this ZIP. The ZIP is arranged so `app.py`, `requirements.txt`, `core/`, `tests/`, and `.streamlit/` are directly at the extracted root; there is no extra nested project folder.
2. Create a GitHub repository. Keep in mind that a public repository exposes the source code; **never upload passwords, secrets, personal photos, or database files**.
3. Upload the extracted project files so `app.py`, `requirements.txt`, `README.md`, `core/`, and `.streamlit/` are at the repository root. Use GitHub Desktop if you want an easier way to publish a full folder.

### 2. Deploy the app

1. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) using the account workflow it requires.
2. Choose **Create app** and select the repository and branch you created.
3. Set the main file path to `app.py`.
4. Open **Advanced settings** and select Python 3.12 if prompted.
5. In the **Secrets** box, set a long, unique password like this (replace the example value):

   ```toml
   APP_PASSWORD = "replace-with-a-long-unique-passphrase"
   ```

   Never commit this value to GitHub. Streamlit provides a secrets panel for this purpose: <https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management>.

6. Deploy. The first build downloads dependencies. The first image analysis also downloads the model and may take several minutes.
7. Open the generated `https://<your-app-name>.streamlit.app` URL on your phone, tablet, or any computer. Enter your app password.

Official deployment guide: <https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy>.

## How to use the online camera

1. Open the deployed app using its HTTPS URL.
2. Select **Vision** → **Use this device's camera**.
3. Approve browser camera permission when prompted and capture a still image. Upload a file instead if the camera option isn't available.
4. Select a task and click **Analyze image**.
5. If needed, manually select a fictional person to save the reviewed description as a memory.

The phone or laptop camera is captured **in the browser** and the image bytes are sent to the hosted app for inference. The image is not intentionally written to disk by this app, but the hosting platform processes it. Do not use this for photos of people without their permission.

## Model and resource notes

- Model: `HuggingFaceTB/SmolVLM-256M-Instruct` (Apache-2.0 model card: <https://huggingface.co/HuggingFaceTB/SmolVLM-256M-Instruct>).
- It runs on cloud CPU by default, no local Ollama install or API token is required for downloading this public model.
- The first inference may be slow due to model download and cold loading. Small images and a short output limit reduce resource use but don't guarantee a particular response time.
- Streamlit Community Cloud has resource limits, so if the instance runs out of memory, use a hosted model-inference service or a hosting platform with more compute. Limits can change: <https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app>.

## Security and data

This is a shared-passphrase demo, **not individual authentication**. Everyone who knows the passphrase can access the shared vault. The app currently has no roles, account-specific databases, encrypted clinical storage, or guaranteed durable backing database. Do not use identifiable health records. For real cross-device memory persistence, add user accounts and a managed database with per-user access policies before deployment.
