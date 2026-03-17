
import os

path = r"c:\My_Projects\MediaManagerX\MediaManagerX\native\mediamanagerx_app\main.py"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Fix _do_full_scan image_exts
old_scan_exts = 'image_exts = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}'
new_scan_exts = 'image_exts = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".avif"}'
if old_scan_exts in content:
    content = content.replace(old_scan_exts, new_scan_exts)
    print("Updated _do_full_scan extensions.")
else:
    print("Could not find _do_full_scan extensions (might already be updated or changed).")

# 2. Restore corrupted metadata section
# We'll search for the start of the corrupted block and the resumption point.
start_anchor = '    def _is_metadata_enabled(self, key: str, default: bool = True) -> bool:\n        """Read metadata visibility setting with robust boolean conversion."""\n        try:\n            qkey = f"metadata/display/{key}"'
end_anchor = '    def _metadata_default_group_order(self, kind: str) -> list[str]:'

# The corrupted content currently looks like (roughly):
# try:
#     qkey = f"metadata/display/{key}"
#     return {
#         "general": [...],
#         "ai": image_ai,
#     }
# return {"general": image_general, "camera": image_camera, "ai": image_ai}

# We'll use a regex-like approach to find the block between start_anchor and end_anchor
import re
pattern = re.escape(start_anchor) + r".*?" + re.escape(end_anchor)
replacement = start_anchor + """
            # Ensure we have the latest from disk
            self.bridge.settings.sync()
            val = self.bridge.settings.value(qkey)
            if val is None:
                return default
            # Handle PySide6/Qt behavior on different platforms
            if isinstance(val, str):
                return val.lower() in ("true", "1")
            return bool(val)
        except Exception:
            return default

    def _metadata_kind_for_path(self, path: str | None) -> str:
        if not path:
            return "image"
        p = Path(path)
        if self.bridge._is_animated(p):
            return "gif"
        if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".avif"}:
            return "image"
        return "video"

    def _metadata_group_fields(self, kind: str) -> dict[str, list[str]]:
        image_general = ["res", "size", "description", "tags", "notes", "embeddedtags", "embeddedcomments"]
        image_camera = ["camera", "location", "iso", "shutter", "aperture", "software", "lens", "dpi"]
        image_ai = [
            "aistatus", "aisource", "aifamilies", "aidetectionreasons", "ailoras", "aimodel", "aicheckpoint",
            "aisampler", "aischeduler", "aicfg", "aisteps", "aiseed", "aiupscaler", "aidenoise",
            "aiprompt", "ainegprompt", "aiparams", "aiworkflows", "aiprovenance", "aicharcards", "airawpaths",
        ]
        if kind == "video":
            return {
                "general": ["res", "size", "duration", "fps", "codec", "audio", "description", "tags", "notes"],
                "ai": image_ai,
            }
        if kind == "gif":
            return {
                "general": ["res", "size", "duration", "fps", "description", "tags", "notes", "embeddedtags", "embeddedcomments"],
                "ai": image_ai,
            }
        return {"general": image_general, "camera": image_camera, "ai": image_ai}\n\n    """ + end_anchor

if re.search(pattern, content, re.DOTALL):
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    print("Restored corrupted metadata section.")
else:
    print("Could not find anchor for metadata section restoration.")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patching complete.")
