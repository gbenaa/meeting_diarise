import argparse
import json
import os

import torch
import whisperx
from whisperx.diarize import DiarizationPipeline


# ========== Helpers ==========

def fmt_ts(seconds: float) -> str:
    if seconds is None:
        seconds = 0.0
    total_ms = int(round(float(seconds) * 1000))
    hours = total_ms // 3600000
    minutes = (total_ms % 3600000) // 60000
    secs = (total_ms % 60000) // 1000
    millis = total_ms % 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def print_segment(prefix: str, seg: dict) -> None:
    start = fmt_ts(seg.get("start", 0))
    end = fmt_ts(seg.get("end", 0))
    text = (seg.get("text") or "").strip()
    speaker = seg.get("speaker")
    if speaker:
        print(f"{prefix}[{start} - {end}] {speaker}: {text}", flush=True)
    else:
        print(f"{prefix}[{start} - {end}] {text}", flush=True)


# ========== Main ==========

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_audio")
    parser.add_argument("output_prefix")
    parser.add_argument("--model", default="large-v3")
    parser.add_argument("--compute-type", default="float16")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--language", default=None)
    parser.add_argument("--num-speakers", type=int, default=2)
    args = parser.parse_args()

    input_audio = args.input_audio
    output_prefix = args.output_prefix

    output_dir = os.path.dirname(output_prefix)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"

    print("[INFO] ==================================================", flush=True)
    print("[INFO] Meeting transcription + diarisation pipeline", flush=True)
    print(f"[INFO] Input:  {input_audio}", flush=True)
    print(f"[INFO] Output: {output_prefix}.txt and {output_prefix}.json", flush=True)
    print(f"[INFO] Device: {device}", flush=True)
    print("[INFO] ==================================================", flush=True)

    print("[INFO] Stage 1/6 -> Loading audio for WhisperX", flush=True)
    audio = whisperx.load_audio(input_audio)

    print("[INFO] Stage 2/6 -> Loading WhisperX model", flush=True)
    model = whisperx.load_model(
        args.model,
        device,
        compute_type=args.compute_type,
        language=args.language,
    )

    print("[INFO] Stage 3/6 -> Transcribing", flush=True)
    result = model.transcribe(audio, batch_size=args.batch_size)

    detected_language = result.get("language")
    if detected_language:
        print(f"[INFO] Detected language -> {detected_language}", flush=True)

    print("[INFO] Transcript segments after transcription", flush=True)
    for seg in result.get("segments", []):
        print_segment("[TRANSCRIBE] ", seg)

    print("[INFO] Stage 4/6 -> Loading alignment model", flush=True)
    model_a, metadata = whisperx.load_align_model(
        language_code=detected_language or args.language or "en",
        device=device,
    )

    print("[INFO] Stage 4/6 -> Aligning transcript", flush=True)
    aligned = whisperx.align(
        result["segments"],
        model_a,
        metadata,
        audio,
        device,
        return_char_alignments=False,
    )

    print("[INFO] Stage 5/6 -> Loading diarisation model", flush=True)
    diarize_model = DiarizationPipeline(
        token=os.environ.get("HF_TOKEN"),
        device=device,
    )

    print("[INFO] Stage 5/6 -> Running diarisation", flush=True)
    diarize_segments = diarize_model(audio, num_speakers=args.num_speakers)

    print("[INFO] Stage 6/6 -> Assigning speakers", flush=True)
    final_result = whisperx.assign_word_speakers(diarize_segments, aligned)

    print("[INFO] Speaker-labelled transcript", flush=True)
    for seg in final_result.get("segments", []):
        print_segment("[DIARISED] ", seg)

    txt_path = f"{output_prefix}.txt"
    json_path = f"{output_prefix}.json"

    with open(txt_path, "w", encoding="utf-8") as f:
        for seg in final_result.get("segments", []):
            start = fmt_ts(seg.get("start", 0))
            end = fmt_ts(seg.get("end", 0))
            speaker = seg.get("speaker", "Speaker ?")
            text = (seg.get("text") or "").strip()
            f.write(f"[{start} - {end}] {speaker}: {text}\n")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(final_result, f, ensure_ascii=False, indent=2)

    print(f"[INFO] Wrote transcript -> {txt_path}", flush=True)
    print(f"[INFO] Wrote JSON -> {json_path}", flush=True)
    print("[INFO] Done", flush=True)


if __name__ == "__main__":
    main()
