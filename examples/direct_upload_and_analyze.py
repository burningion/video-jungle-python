"""
Direct S3 upload + analysis example

Usage:
  - Set your API key: export VJ_API_KEY=... 
  - Run: python examples/direct_upload_and_analyze.py /path/to/video.mp4 --name "My Upload" [--subscribe]

What it does:
  1) Creates a video record with upload_method="direct" to get a presigned POST
  2) Uploads the file bytes to S3 using the presigned form
  3) Starts analysis for the created video
  4) Optionally subscribes to status updates via SSE
"""

import argparse
import json
import os
import sys
from typing import Any, Dict

import requests

from videojungle import ApiClient


def _extract_upload_info(obj: Dict[str, Any]) -> Dict[str, Any]:
    """Find the presigned POST payload in the response.

    Expected shapes include one of:
      { "upload_url": { "url": ..., "fields": {...} }, "video": {"id": ...} }
      { "video": { "id": ..., "upload_url": { "url": ..., "fields": {...} } } }
    """
    if not isinstance(obj, dict):
        raise ValueError("Unexpected response payload; expected a dict.")

    upload_url = obj.get("upload_url")
    if isinstance(upload_url, dict) and "url" in upload_url and "fields" in upload_url:
        return upload_url

    video = obj.get("video", {}) if isinstance(obj.get("video"), dict) else {}
    upload_url = video.get("upload_url")
    if isinstance(upload_url, dict) and "url" in upload_url and "fields" in upload_url:
        return upload_url

    raise KeyError("Could not find presigned upload_url in API response.")


def _extract_video_id(obj: Dict[str, Any]) -> str:
    """Extract the created video id from the API response."""
    if isinstance(obj, dict):
        video = obj.get("video")
        if isinstance(video, dict) and "id" in video:
            return str(video["id"])
        if "id" in obj:
            return str(obj["id"])
    raise KeyError("Could not find video id in API response.")


def upload_via_presigned_post(file_path: str, upload_info: Dict[str, Any]) -> None:
    """Upload the file to S3 using a presigned POST payload."""
    url = upload_info["url"]
    fields = upload_info.get("fields", {})

    filename = os.path.basename(file_path)
    content_type = fields.get("Content-Type") or "application/octet-stream"

    with open(file_path, "rb") as f:
        resp = requests.post(
            url,
            data=fields,
            files={"file": (filename, f, content_type)},
        )

    if resp.status_code not in (200, 201, 204):
        # S3 may return an XML error body when something goes wrong
        snippet = resp.text[:300].replace("\n", " ")
        raise RuntimeError(f"S3 upload failed ({resp.status_code}): {snippet}")


def subscribe_sse(base_url: str, video_id: str, token: str) -> None:
    """Subscribe to SSE updates for the given video id.

    Endpoint: GET /videos/{video_id}/subscribe
    """
    url = f"{base_url}/videos/{video_id}/subscribe"
    headers = {
        "Accept": "text/event-stream",
        "Cache-Control": "no-cache",
        "X-API-Key": token,
    }
    with requests.get(url, headers=headers, stream=True, timeout=60) as r:
        r.raise_for_status()
        print("Subscribed to status updates (Ctrl-C to exit) ...")
        for raw in r.iter_lines(decode_unicode=True):
            if raw is None:
                continue
            line = raw.strip()
            if not line or line.startswith(":"):
                # comment/keepalive
                continue
            if line.startswith("data:"):
                data = line[len("data:"):].strip()
                try:
                    obj = json.loads(data)
                    print(f"SSE data: {json.dumps(obj, ensure_ascii=False)}")
                except Exception:
                    print(f"SSE data: {data}")
            else:
                # Other SSE fields like event:, id:, retry:
                print(line)


def main() -> int:
    parser = argparse.ArgumentParser(description="Direct upload to S3 and start analysis")
    parser.add_argument("file", help="Path to local video file")
    parser.add_argument("--name", help="Display name for the video (defaults to filename)")
    parser.add_argument("--subscribe", action="store_true", help="Subscribe to status updates via SSE")
    args = parser.parse_args()

    api_key = os.environ.get("VJ_API_KEY")
    if not api_key:
        print("Please set VJ_API_KEY in your environment", file=sys.stderr)
        return 2

    file_path = os.path.expanduser(args.file)
    if not os.path.isfile(file_path):
        print(f"File not found: {file_path}", file=sys.stderr)
        return 2

    display_name = args.name or os.path.basename(file_path)

    # Initialize API client
    vj = ApiClient(token=api_key)

    print("Requesting presigned POST for direct upload ...")
    # Note: run_analysis=False because we will start analysis after upload completes
    create_resp = vj.video_files.create(
        name=display_name,
        filename=os.path.basename(file_path),
        upload_method="direct",
        run_analysis=False,
    )

    try:
        upload_info = _extract_upload_info(create_resp)
        video_id = _extract_video_id(create_resp)
    except Exception as e:
        print(f"Failed to parse create response: {e}", file=sys.stderr)
        return 1

    print(f"Uploading '{file_path}' to S3 ...")
    upload_via_presigned_post(file_path, upload_info)
    print("Upload complete.")

    print("Starting analysis ...")
    vj.video_files.create_analysis(video_id)
    print(f"Analysis started for video id: {video_id}")

    if args.subscribe:
        try:
            subscribe_sse(vj.BASE_URL, video_id, api_key)
        except KeyboardInterrupt:
            print("\nSSE subscription stopped by user.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

