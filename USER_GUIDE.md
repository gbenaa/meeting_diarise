# User Guide

## Purpose

This guide explains how to run the meeting diarisation pipeline and where to find outputs.

## 1. Prepare the input

Put the meeting recording at:

```text
input/meeting.mp3
```

## 2. Set the Hugging Face token

Export the token in the shell before running:

```bash
export HF_TOKEN="your_token_here"
```

This token must have access to the required gated diarisation models.

## 3. Build the image

Rebuild only when one of these changes:

- `Dockerfile`
- `requirements.txt`

Command:

```bash
docker build --network host --no-cache -t meeting-diariser:stable .
```

## 4. Run the pipeline

```bash
./run_pipeline_hostnet.sh
```

## 5. Watch progress

The script prints:

- stage messages
- transcript segments after transcription
- speaker-labelled segments after diarisation

A dated log file is also written to:

```text
output/logs/
```

## 6. Find the outputs

Final outputs should appear at:

```text
output/meeting.txt
output/meeting.json
```

## 7. When rebuilds are not needed

You do not need to rebuild when changing:

- `diarise.py`
- `run_pipeline_hostnet.sh`

This is because:

- `run_pipeline_hostnet.sh` runs on the host
- `diarise.py` is mounted into the container at runtime

## 8. When rebuilds are needed

Rebuild when changing:

- `Dockerfile`
- `requirements.txt`

## 9. Cache locations

Mounted caches:

- Hugging Face cache:
  - `hf_cache/`
- Torch / alignment-model cache:
  - `torch_cache/`

These are persisted across runs.

## 10. Logs

Each run writes a dated log file to:

```text
output/logs/
```

Useful checks:

```bash
ls -lh output
ls -lh output/logs
tail -n 50 output/logs/<latest_log>
```

## 11. Development workflow

Normal development loop:

1. Edit `diarise.py`
2. Run `./run_pipeline_hostnet.sh`
3. Inspect console output and `output/logs/`
4. Repeat

No rebuild is needed unless dependencies change.
