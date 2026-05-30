import json

log_path = "/Users/Janet/.gemini/antigravity/brain/a7f48d67-3cec-4270-ba1f-2c2ce67ea3d1/.system_generated/logs/transcript.jsonl"

with open(log_path, 'r') as f:
    for line in f:
        obj = json.loads(line)
        if obj.get("step_index") == 635:
            content = obj.get("content", "")
            # Find the index of BUILD_STATUS.md
            idx = content.find("BUILD_STATUS.md")
            if idx != -1:
                # Print from 1000 chars before to 3000 chars after
                start = max(0, idx - 1000)
                end = min(len(content), idx + 3000)
                print(content[start:end])
            else:
                print("Not found")
            break
