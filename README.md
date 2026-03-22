# Meeting Diarisation Pipeline

A Docker-based pipeline for transcribing and diarising a single mixed meeting recording.

## What it does

This project:

- takes one mixed MP3 recording
- transcribes speech with WhisperX
- aligns the transcript
- diarises the speakers
- produces speaker-labelled output
- prints transcript progress to the console during the run

## Current operating model

The Docker image contains the runtime environment and dependencies.

The host provides:

- `diarise.py`
- `run_pipeline_hostnet.sh`
- `input/`
- `output/`
- `hf_cache/`
- `torch_cache/`

`diarise.py` is mounted into the container at runtime, so it can be edited without rebuilding the image.

## Requirements

- Linux host
- Docker
- NVIDIA Container Toolkit / GPU-enabled Docker
- Hugging Face token with access to the required gated models
- Network access for first-time model downloads

## Directory layout

```text
meeting_diarise/
├── Dockerfile
├── requirements.txt
├── diarise.py
├── run_pipeline_hostnet.sh
├── README.md
├── USER_GUIDE.md
├── TROUBLESHOOTING.md
├── .gitignore
├── input/
├── output/
├── hf_cache/
└── torch_cache/
```

## Build

Rebuild only when `Dockerfile` or `requirements.txt` changes.

```bash
docker build --network host --no-cache -t meeting-diariser:stable .
```

## Run

```bash
export HF_TOKEN="your_token_here"
./run_pipeline_hostnet.sh
```

## Input

Place the meeting recording at:

```text
input/meeting.mp3
```

## Output

Expected outputs:

```text
output/meeting.txt
output/meeting.json
```

Logs are written to:

```text
output/logs/
```

## Notes

- This host currently requires `--network host` because Docker bridge networking was not working correctly.
- The first successful run may download WhisperX and alignment models.
- Subsequent runs should reuse the mounted caches in `hf_cache/` and `torch_cache/`.

See `USER_GUIDE.md` for normal operation and `TROUBLESHOOTING.md` for known issues.
