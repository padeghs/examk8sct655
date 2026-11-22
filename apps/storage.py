import json
import fcntl
import os
from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path
from tempfile import NamedTemporaryFile

from pythainlp.tokenize import word_tokenize

MIN_WORDS = 300
LIMIT = 500
DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
ARTICLE = DATA_DIR / "research.txt"
SEED = Path(__file__).with_name("seed.txt")


def tokens(text):
    return word_tokenize(text, engine="newmm", keep_whitespace=True)


def is_word(token):
    return any(char.isalnum() for char in token)


def word_count(text):
    return sum(is_word(token) for token in tokens(text))


def display_text(text):
    parts = []
    count = 0
    for token in tokens(text):
        count += is_word(token)
        if count > LIMIT:
            return "".join(parts).rstrip() + "…"
        parts.append(token)
    return text


@contextmanager
def locked():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with (DATA_DIR / ".research.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def _write_atomic(text, destination=ARTICLE):
    with NamedTemporaryFile(mode="w", encoding="utf-8", dir=DATA_DIR, delete=False) as file:
        temp = Path(file.name)
        try:
            file.write(text)
            file.flush()
            os.fsync(file.fileno())
            os.replace(temp, destination)
        finally:
            temp.unlink(missing_ok=True)


def read_article():
    try:
        return ARTICLE.read_text(encoding="utf-8")
    except FileNotFoundError:
        return SEED.read_text(encoding="utf-8")


def revision(text):
    return sha256(text.encode("utf-8")).hexdigest()


def save_article(text, previous_revision):
    with locked():
        if revision(read_article()) != previous_revision:
            return False
        _write_atomic(text)
        return True


PROFILE = DATA_DIR / "profile.json"
DEFAULT_PROFILE = {"name": "เผด็จ แสงบุษราคัม", "student_id": "68130039"}


def read_profile():
    try:
        return json.loads(PROFILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return DEFAULT_PROFILE.copy()


def save_profile(profile, previous_revision):
    with locked():
        if profile_revision(read_profile()) != previous_revision:
            return False
        _write_atomic(json.dumps(profile, ensure_ascii=False), PROFILE)
        return True


def profile_revision(profile):
    return revision(json.dumps(profile, sort_keys=True))
