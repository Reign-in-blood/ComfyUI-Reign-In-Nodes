import { app } from "../../scripts/app.js";

const NODE_ID = "RIN_RandomCharacter";
const PREVIEW_WIDGET = "rin_preview_text";
const SAFE_SEED_MAX = 1125899906842624;

function getMode(widget) {
    const value = widget?.value;
    if (typeof value === "string") return value;
    if (value && typeof value === "object") {
        return value.mode ?? value.value ?? value.name ?? "";
    }
    return "";
}

function isRandomMode(node) {
    const modeWidget = node.widgets?.find((widget) => widget?.name === "mode");
    return getMode(modeWidget) === "Random";
}

function setHidden(widget, hidden) {
    if (!widget) return;
    widget.hidden = hidden;
}

function getSeedWidget(node) {
    return node.widgets?.find((widget) => widget?.name === "seed") ?? null;
}

function getSeedControl(node, seedWidget) {
    const linked = (seedWidget?.linkedWidgets ?? []).find(
        (widget) =>
            widget?.name === "control_after_generate" &&
            (typeof widget.beforeQueued === "function" ||
                typeof widget.afterQueued === "function")
    );
    if (linked) return linked;

    const native = (node.widgets ?? []).find(
        (widget) =>
            widget?.name === "control_after_generate" &&
            (typeof widget.beforeQueued === "function" ||
                typeof widget.afterQueued === "function")
    );
    if (native) return native;

    return (
        (seedWidget?.linkedWidgets ?? []).find(
            (widget) => widget?.name === "control_after_generate"
        ) ??
        (node.widgets ?? []).find(
            (widget) => widget?.name === "control_after_generate"
        ) ??
        null
    );
}

function numericSeed(seedWidget) {
    const value = Number(seedWidget?.value);
    if (!Number.isFinite(value)) return 0;
    return Math.max(0, Math.min(Math.trunc(value), SAFE_SEED_MAX));
}

function nextSeed(seedWidget, controlMode) {
    const current = numericSeed(seedWidget);
    const rawMax = Number(seedWidget?.options?.max);
    const max = Number.isFinite(rawMax)
        ? Math.max(0, Math.min(rawMax, SAFE_SEED_MAX))
        : SAFE_SEED_MAX;

    switch (controlMode) {
        case "increment":
            return Math.min(current + 1, max);
        case "decrement":
            return Math.max(current - 1, 0);
        case "randomize":
            return Math.floor(Math.random() * (max + 1));
        default:
            return current;
    }
}

function writeSeed(seedWidget, value) {
    seedWidget.value = value;
    seedWidget.callback?.(value);
}

function repairNativeSeedControl(node) {
    const seedWidget = getSeedWidget(node);
    if (!seedWidget) return;

    const control = getSeedControl(node, seedWidget);
    if (!control) return;

    // A restored workflow can keep the visible control while losing the
    // target->control link used by ComfyUI's value-control code. Restore that
    // link without creating another widget.
    seedWidget.linkedWidgets = [control];

    if (control.__rinSeedRepairInstalled) return;
    control.__rinSeedRepairInstalled = true;

    const nativeBeforeQueued = control.beforeQueued;
    const nativeAfterQueued = control.afterQueued;
    let changedBeforeQueue = false;

    control.beforeQueued = function (...args) {
        const before = numericSeed(seedWidget);
        const result = nativeBeforeQueued?.apply(this, args);
        changedBeforeQueue = numericSeed(seedWidget) !== before;
        return result;
    };

    control.afterQueued = function (...args) {
        const before = numericSeed(seedWidget);
        const result = nativeAfterQueued?.apply(this, args);
        const changedAfterQueue = numericSeed(seedWidget) !== before;

        // Native ComfyUI remains authoritative. The fallback runs only when
        // its callback did not change the seed at all (the failure observed on
        // restored/custom V3 nodes).
        if (
            isRandomMode(node) &&
            control.value !== "fixed" &&
            !changedBeforeQueue &&
            !changedAfterQueue
        ) {
            writeSeed(seedWidget, nextSeed(seedWidget, control.value));
        }

        changedBeforeQueue = false;
        return result;
    };
}

function refitNode(node) {
    requestAnimationFrame(() => {
        const size = node.computeSize?.([...node.size]);
        if (!size) return;
        const width = Math.max(node.size?.[0] ?? size[0], 320);
        node.setSize?.([width, size[1]]);
        node.graph?.setDirtyCanvas?.(true, true);
    });
}

function addPreview(node) {
    if (node.widgets?.some((widget) => widget?.name === PREVIEW_WIDGET)) return;
    if (typeof node.addDOMWidget !== "function") return;

    const box = document.createElement("textarea");
    box.readOnly = true;
    box.placeholder = "Text preview";
    box.spellcheck = false;
    box.style.boxSizing = "border-box";
    box.style.width = "100%";
    box.style.height = "100%";
    box.style.minHeight = "84px";
    box.style.resize = "none";
    box.style.padding = "8px";
    box.style.borderRadius = "6px";
    box.style.border = "1px solid var(--border-color, #555)";
    box.style.background = "var(--comfy-input-bg, rgba(0, 0, 0, 0.25))";
    box.style.color = "var(--input-text, inherit)";
    box.style.font = "12px/1.35 monospace";
    box.style.whiteSpace = "pre-wrap";

    let previewValue = "";
    const widget = node.addDOMWidget(PREVIEW_WIDGET, "text", box, {
        hideOnZoom: false,
        getMinHeight: () => 100,
        getMaxHeight: () => 260,
        getHeight: () => 110,
        getValue: () => previewValue,
        setValue: (value) => {
            previewValue = value == null ? "" : String(value);
            box.value = previewValue;
        },
    });
    widget.serialize = false;
    widget.options.serialize = false;
    node.__rinRandomCharacterPreview = widget;

    refitNode(node);
}

function textFromExecution(message) {
    const value = message?.text;
    if (value == null) return "";
    if (Array.isArray(value)) {
        return value
            .filter((part) => part != null)
            .map((part) => String(part))
            .join("\n\n");
    }
    return String(value);
}

function updatePreview(node, message) {
    const widget =
        node.__rinRandomCharacterPreview ??
        node.widgets?.find((candidate) => candidate?.name === PREVIEW_WIDGET);
    if (!widget) return;
    widget.value = textFromExecution(message);
}

function refreshVisibility(node) {
    const seedWidget = getSeedWidget(node);
    if (!seedWidget) return;

    repairNativeSeedControl(node);
    const control = getSeedControl(node, seedWidget);
    const hidden = !isRandomMode(node);

    setHidden(seedWidget, hidden);
    setHidden(control, hidden);
    refitNode(node);
}

app.registerExtension({
    name: "Reign-In-Nodes.RandomCharacterUI",

    nodeCreated(node) {
        if (node.comfyClass !== NODE_ID) return;

        addPreview(node);

        const originalOnExecuted = node.onExecuted;
        node.onExecuted = function (message) {
            originalOnExecuted?.apply(this, arguments);
            updatePreview(this, message);
        };

        requestAnimationFrame(() => {
            const modeWidget = node.widgets?.find((widget) => widget?.name === "mode");
            if (!modeWidget) return;

            const originalCallback = modeWidget.callback;
            modeWidget.callback = function (...args) {
                const result = originalCallback?.apply(this, args);
                requestAnimationFrame(() => refreshVisibility(node));
                return result;
            };

            repairNativeSeedControl(node);
            refreshVisibility(node);
        });
    },
});
