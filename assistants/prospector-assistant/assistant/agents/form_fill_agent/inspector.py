import contextlib
import json
from pathlib import Path
from typing import Callable

import yaml
from semantic_workbench_assistant.assistant_app.context import ConversationContext
from semantic_workbench_assistant.assistant_app.protocol import (
    AssistantConversationInspectorStateDataModel,
    ReadOnlyAssistantConversationInspectorStateProvider,
)

from . import gce, state


class FileStateInspector(ReadOnlyAssistantConversationInspectorStateProvider):
    def __init__(
        self, display_name: str, file_path_source: Callable[[ConversationContext], Path], description: str = ""
    ) -> None:
        self._display_name = display_name
        self._file_path_source = file_path_source
        self._description = description

    @property
    def display_name(self) -> str:
        return self._display_name

    @property
    def description(self) -> str:
        return self._description

    async def get(self, context: ConversationContext) -> AssistantConversationInspectorStateDataModel:
        def read_state(path: Path) -> dict:
            with contextlib.suppress(FileNotFoundError):
                return json.loads(path.read_text(encoding="utf-8"))
            return {}

        state = read_state(self._file_path_source(context))

        # return the state as a yaml code block, as it is easier to read than json
        return AssistantConversationInspectorStateDataModel(
            data={"content": f"```yaml\n{yaml.dump(state, sort_keys=False)}\n```"},
        )


FormFillAgentStateInspector = FileStateInspector(
    display_name="Form Fill Agent State", file_path_source=state.path_for_state
)
AcquireFormGuidedConversationStateInspector = FileStateInspector(
    display_name="Acquire Form Guided Conversation State",
    file_path_source=lambda context: gce.path_for_guided_conversation_state(
        context, state.FormFillAgentMode.acquire_form_step
    ),
)
FillFormGuidedConversationStateInspector = FileStateInspector(
    display_name="Fill Form Guided Conversation State",
    file_path_source=lambda context: gce.path_for_guided_conversation_state(
        context, state.FormFillAgentMode.fill_form_step
    ),
)
