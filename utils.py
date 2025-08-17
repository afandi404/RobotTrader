import time, json, logging, os
from datetime import datetime, timezone

def utc_now_ms():
    return int(datetime.now(timezone.utc).timestamp()*1000)

def sleep_s(seconds):
    time.sleep(seconds)

def human_ts(ms):
    return datetime.fromtimestamp(ms/1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

def setup_logger(level='INFO'):
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format='[%(asctime)s] %(levelname)s - %(message)s',
    )
    return logging.getLogger("bot")

def jlog(path, rec):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'a') as f:
        f.write(json.dumps(rec)+"\n")