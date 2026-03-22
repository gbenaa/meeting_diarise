# Troubleshooting

## 1. Docker container cannot reach the internet

### Symptom

Requests to external sites fail from inside the container.

### Cause

Docker bridge networking on this host is not functioning correctly.

### Fix

Use host networking for both build and run:

```bash
docker build --network host --no-cache -t meeting-diariser:stable .
./run_pipeline_hostnet.sh
```

## 2. WhisperX / faster-whisper compatibility error

### Symptom

Error mentioning `TranscriptionOptions.__new__()` and missing arguments such as:

- `max_new_tokens`
- `clip_timestamps`
- `hallucination_silence_threshold`

### Cause

Version mismatch between WhisperX and faster-whisper.

### Fix

Pin compatible versions in `requirements.txt`, then rebuild.

## 3. Transcript printed to console but no output file written

### Symptom

Transcript segments appear in the console, but `output/meeting.txt` is missing.

### Cause

The pipeline crashed before the final write stage.

### Check

Inspect the latest log:

```bash
ls -1t output/logs | head
tail -n 50 output/logs/<latest_log>
```

## 4. `module 'whisperx' has no attribute 'DiarizationPipeline'`

### Cause

The current WhisperX version expects diarisation import from:

```python
from whisperx.diarize import DiarizationPipeline
```

not from `whisperx.DiarizationPipeline`.

### Fix

Update `diarise.py` accordingly.

## 5. GPU display goes black during processing

### Possible causes

- the display is using the same GPU as the compute workload
- GPU memory pressure
- driver or display instability under heavy load

### Mitigations

- avoid using the display GPU if another GPU is available
- reduce model size
- reduce batch size
- run from SSH where possible
- monitor with `nvidia-smi`

## 6. `GPU device discovery failed`

### Meaning

This warning usually comes from `onnxruntime` and is not necessarily fatal.

If the pipeline continues through transcription, alignment, and diarisation, this warning can often be ignored.

## 7. Hugging Face model access issues

### Cause

- missing token
- token not exported in shell
- access not granted for gated model

### Fix

```bash
export HF_TOKEN="your_token_here"
```

and ensure the token owner has accepted the gated model access conditions.

## 8. Input file not found

### Symptom

Errors like:

```text
/input/meeting.mp3: No such file or directory
```

### Cause

The input file is missing or the volume mount is wrong.

### Fix

Ensure the host file exists:

```bash
ls -lh input/meeting.mp3
```

## 9. Changing `diarise.py` has no effect

### Cause

The file may not be mounted into the container.

### Fix

Confirm `run_pipeline_hostnet.sh` contains:

```bash
-v "$(pwd)/diarise.py:/app/diarise.py:ro"
--entrypoint python3
meeting-diariser:stable \
/app/diarise.py /input/meeting.mp3 /output/meeting
```
