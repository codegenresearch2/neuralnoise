import json
import os
from typing import Any, Callable

from autogen import (  # type: ignore
    Agent,
    AssistantAgent,
    GroupChat,
    GroupChatManager,
    UserProxyAgent,
)

from neuralnoise.studio.hooks import (
    optimize_chat_history_hook,
    save_last_json_message_hook,
)
from neuralnoise.studio.utils import load_prompt
from neuralnoise.types import StudioConfig


def agent(func: Callable) -> Callable:
    func.is_agent = True

    return func


class PodcastStudio:
    def __init__(self, name: str, config: StudioConfig, max_round: int = 50):
        self.name = name
        self.config = config
        self.language = config.show.language
        self.max_round = max_round

        self.llm_default_config = {
            "model": "gpt-4o",
            "api_key": os.environ["OPENAI_API_KEY"],
        }

        self.llm_json_mode_config = {
            "response_format": {"type": "json_object"},
            "model": "gpt-4o",
            "api_key": os.environ["OPENAI_API_KEY"],
        }

        self.agents: list[Agent] = []
        for attr in dir(self):
            if hasattr(getattr(self, attr), "is_agent"):
                self.agents.append(getattr(self, attr)())

    @agent
    def content_analyzer_agent(self) -> AssistantAgent:
        agent = AssistantAgent(
            name="ContentAnalyzerAgent",
            system_message=load_prompt(
                "content_analyzer.system", language=self.language
            ),
            llm_config=self.llm_json_mode_config,
        )
        agent.register_hook(
            hookable_method="process_message_before_send",
            hook=save_last_json_message_hook(
                "content_analyzer", f"output/{self.name}/analyzer/"
            ),
        )

        return agent

    @agent
    def planner_agent(self) -> AssistantAgent:
        return AssistantAgent(
            name="PlannerAgent",
            system_message=load_prompt("planner.system", language=self.language),
            llm_config=self.llm_default_config,
        )

    @agent
    def script_generator_agent(self) -> AssistantAgent:
        agent = AssistantAgent(
            name="ScriptGeneratorAgent",
            system_message=load_prompt(
                "script_generation.system", language=self.language
            ),
            llm_config=self.llm_json_mode_config,
        )
        agent.register_hook(
            hookable_method="process_message_before_send",
            hook=save_last_json_message_hook(
                "script_generator", f"output/{self.name}/scripts/"
            ),
        )
        agent.register_hook(
            hookable_method="process_all_messages_before_reply",
            hook=optimize_chat_history_hook,
        )

        return agent

    @agent
    def editor_agent(self) -> AssistantAgent:
        agent = AssistantAgent(
            name="EditorAgent",
            system_message=load_prompt("editor.system", language=self.language),
            llm_config=self.llm_default_config,
        )
        agent.register_hook(
            hookable_method="process_all_messages_before_reply",
            hook=optimize_chat_history_hook,
        )

        return agent

    def generate_script(self, content: str) -> dict[str, Any]:
        def is_termination_msg(message):
            return isinstance(message, dict) and (
                message.get("content", "") == ""
                or message.get("content", "").rstrip().endswith("TERMINATE")
            )

        user_proxy = UserProxyAgent(
            name="UserProxy",
            system_message=load_prompt("user_proxy.system"),
            human_input_mode="TERMINATE",
            code_execution_config=False,
        )

        groupchat = GroupChat(
            agents=self.agents,
            messages=[],
            max_round=self.max_round,
        )

        manager = GroupChatManager(
            groupchat=groupchat,
            llm_config=self.llm_default_config,
            system_message=load_prompt("manager.system"),
            is_termination_msg=is_termination_msg,
        )

        # Initiate the chat with a clear task description
        user_proxy.initiate_chat(
            manager,
            message=load_prompt(
                "user_proxy.message",
                content=content,
                show=self.config.show_info(),
                speakers=self.config.speakers_info(),
            ),
        )

        # Extract the final script from the chat history
        # TODO: improve this logic
        script_sections: dict[str, Any] = {}
        for script_filepath in sorted(os.listdir(f"output/{self.name}/scripts/")):
            with open(f"output/{self.name}/scripts/{script_filepath}") as f:
                script = json.load(f)
                script_sections[script["section_id"]] = script

        # Combine all approved script sections
        final_script = {
            "messages": groupchat.messages,
            "sections": script_sections,
        }

        return final_script
