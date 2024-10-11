import json
import os
from datetime import datetime
from typing import Any


def save_last_json_message_hook(filename: str, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)

    def hook(sender, message, recipient, silent):
        message_dict = json.loads(message)
        message = json.dumps(message_dict, indent=2)

        date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filepath = os.path.join(output_dir, f"{filename}_{date_str}.json")
        with open(filepath, "w") as f:
            f.write(message)

        return message

    return hook


def optimize_chat_history_hook(
    messages: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    last_messages = {}
    agents_to_keep_last = {"ScriptGeneratorAgent", "EditorAgent", "PlannerAgent"}

    new_messages: list[dict[str, Any]] = []
    for message in reversed(messages):
        agent_name = message["name"]
        if agent_name in agents_to_keep_last:
            if agent_name not in last_messages:
                last_messages[agent_name] = message
                new_messages.append(message)
        else:
            new_messages.append(message)

    print(
        f"On ScriptGeneratorAgent hook, #messages: {len(messages)} "
        f"-> #new-messages: {len(new_messages)}"
    )

    return list(reversed(new_messages))
