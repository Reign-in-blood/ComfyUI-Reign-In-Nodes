from __future__ import annotations

import hashlib
import random
import time
from pathlib import Path

from comfy_api.latest import io, ui

from ..Architecture import icons


LIST_ROOT_DIR_NAME = "lists"
CHARACTER_DIR_NAME = "characters"
MULTI_CHARACTER_SEPARATOR = "\n.\n"
PREFIX_SEPARATOR = ". "
NO_LIST_PLACEHOLDER = "<no character list found>"
EMPTY_LIST_PLACEHOLDER = "<empty character list>"

# Sequential mode deliberately has no visible counter/seed.
# Position is kept per node instance and per selected list for the current ComfyUI session.
_SEQUENCE_POSITIONS: dict[tuple[str, str], int] = {}


def _addon_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _character_list_dir() -> Path:
    return _addon_root() / LIST_ROOT_DIR_NAME / CHARACTER_DIR_NAME


def _safe_list_path(filename: str) -> Path | None:
    if not filename:
        return None

    root = _character_list_dir().resolve()
    candidate = (root / filename).resolve()

    if candidate.suffix.lower() != ".txt":
        return None

    if root != candidate.parent and root not in candidate.parents:
        return None

    return candidate


def _list_character_files() -> list[str]:
    directory = _character_list_dir()
    if not directory.is_dir():
        return []

    return sorted(
        path.name
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() == ".txt"
    )


def _character_files_or_placeholder() -> list[str]:
    return _list_character_files() or [NO_LIST_PLACEHOLDER]


def _load_character_lines(filename: str) -> list[str]:
    path = _safe_list_path(filename)
    if path is None or not path.is_file():
        return []

    lines: list[str] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            lines.append(line)

    return lines


def _character_name(line: str) -> str:
    name = line.split(",", 1)[0].strip()
    return name or line


def _character_entries(filename: str) -> list[tuple[str, str]]:
    lines = _load_character_lines(filename)
    counts: dict[str, int] = {}
    entries: list[tuple[str, str]] = []

    for line in lines:
        name = _character_name(line)
        counts[name] = counts.get(name, 0) + 1
        occurrence = counts[name]
        label = name if occurrence == 1 else f"{name} [{occurrence}]"
        entries.append((label, line))

    return entries


def _character_labels(filename: str) -> list[str]:
    labels = [label for label, _line in _character_entries(filename)]
    return labels or [EMPTY_LIST_PLACEHOLDER]


def _character_list_input() -> io.Combo.Input:
    files = _character_files_or_placeholder()
    return io.Combo.Input(
        "character_list",
        display_name="Character List",
        options=files,
        default=files[0],
        tooltip="Choose the character list.",
    )


def _make_manual_list_options() -> list[io.DynamicCombo.Option]:
    files = _character_files_or_placeholder()

    options: list[io.DynamicCombo.Option] = []
    for filename in files:
        labels = (
            _character_labels(filename)
            if filename != NO_LIST_PLACEHOLDER
            else [EMPTY_LIST_PLACEHOLDER]
        )
        options.append(
            io.DynamicCombo.Option(
                filename,
                [
                    io.Combo.Input(
                        "character",
                        options=labels,
                        default=labels[0],
                        display_name="Character",
                        tooltip="Select a character by the text before the first comma in the list line.",
                    )
                ],
            )
        )

    return options


def _selected_list_data(mode_data: dict) -> tuple[str, dict]:
    list_value = mode_data.get("character_list", "")

    # Manual mode uses a DynamicCombo so the selected character list
    # and the selected character arrive in a nested dictionary.
    if isinstance(list_value, dict):
        filename = str(list_value.get("character_list", ""))
        return filename, list_value

    # Random and Sequential use a regular Combo. Their mode-specific
    # values live directly in the mode dictionary.
    return str(list_value or ""), mode_data


def _join_characters(lines: list[str]) -> str:
    return MULTI_CHARACTER_SEPARATOR.join(lines)


def _join_prefix(prefix: str | None, character_text: str) -> str:
    prefix = (prefix or "").strip()

    if not prefix:
        return character_text
    if not character_text:
        return prefix

    if prefix.endswith("."):
        return f"{prefix} {character_text}"

    return f"{prefix}{PREFIX_SEPARATOR}{character_text}"


class RIN_RandomCharacter(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="RIN_RandomCharacter",
            display_name="🦁 | Random Character",
            category=icons.get("MyNodes/Prompt"),
            description=(
                "Build a character prompt from text lists. "
                "Supports deterministic random selection, automatic sequential selection and manual selection."
            ),
            inputs=[
                io.String.Input(
                    "text",
                    display_name="Text",
                    default="",
                    optional=True,
                    force_input=True,
                    tooltip="Optional text to prepend to the selected character prompt.",
                ),
                io.DynamicCombo.Input(
                    "mode",
                    display_name="Mode",
                    options=[
                        io.DynamicCombo.Option(
                            "Random",
                            [
                                _character_list_input(),
                                io.Int.Input(
                                    "characters",
                                    display_name="Characters",
                                    default=1,
                                    min=1,
                                    max=32,
                                    step=1,
                                    tooltip="Number of distinct character lines to select.",
                                ),
                                io.Int.Input(
                                    "seed",
                                    display_name="Seed",
                                    default=0,
                                    min=0,
                                    max=0xFFFFFFFFFFFFFFFF,
                                    step=1,
                                    control_after_generate=True,
                                    tooltip=(
                                        "Random seed. Fixed reproduces the same selection; "
                                        "randomize, increment and decrement use ComfyUI's native seed control."
                                    ),
                                ),
                            ],
                        ),
                        io.DynamicCombo.Option(
                            "Sequential",
                            [
                                _character_list_input(),
                            ],
                        ),
                        io.DynamicCombo.Option(
                            "Manual",
                            [
                                io.DynamicCombo.Input(
                                    "character_list",
                                    display_name="Character List",
                                    options=_make_manual_list_options(),
                                )
                            ],
                        ),
                    ],
                ),
            ],
            outputs=[
                io.String.Output(display_name="text"),
            ],
            hidden=[
                io.Hidden.unique_id,
            ],
        )

    @classmethod
    def execute(
        cls,
        mode: dict,
        text: str | None = None,
        unique_id=None,
    ) -> io.NodeOutput:
        selected_mode = str(mode.get("mode", "Random"))
        filename, list_data = _selected_list_data(mode)

        if filename in ("", NO_LIST_PLACEHOLDER):
            result = _join_prefix(text, "")
            return io.NodeOutput(result, ui=ui.PreviewText(result))

        lines = _load_character_lines(filename)
        if not lines:
            result = _join_prefix(text, "")
            return io.NodeOutput(result, ui=ui.PreviewText(result))

        selected: list[str]

        if selected_mode == "Random":
            count = max(1, min(int(list_data.get("characters", 1)), len(lines)))
            seed = int(list_data.get("seed", 0))
            rng = random.Random(seed)
            selected = rng.sample(lines, count)

        elif selected_mode == "Sequential":
            key = (str(unique_id), filename)
            start = _SEQUENCE_POSITIONS.get(key, 0) % len(lines)
            selected = [lines[start]]
            _SEQUENCE_POSITIONS[key] = (start + 1) % len(lines)

        elif selected_mode == "Manual":
            requested = str(list_data.get("character", ""))
            entry_map = dict(_character_entries(filename))
            line = entry_map.get(requested)
            selected = [line] if line else []

        else:
            selected = []

        character_text = _join_characters(selected)
        result = _join_prefix(text, character_text)
        return io.NodeOutput(result, ui=ui.PreviewText(result))

    @classmethod
    def fingerprint_inputs(
        cls,
        mode: dict,
        text: str | None = None,
        unique_id=None,
    ):
        selected_mode = str(mode.get("mode", "Random"))
        filename, _list_data = _selected_list_data(mode)
        path = _safe_list_path(filename)

        digest = None
        if path is not None and path.is_file():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()

        if selected_mode == "Sequential":
            # Sequential is intentionally stateful and must execute on every queued generation.
            return (filename, digest, time.time_ns())

        # Random/Manual can be cached normally; prompt inputs already include mode data.
        return (filename, digest)
