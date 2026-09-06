import { app } from "../../scripts/app.js";

const NODE_ID = "RIN_RandomCharacter";

function getMode(widget) {
    const value = widget?.value;
    if (typeof value === "string") return value;
    if (value && typeof value === "object") {
        return value.mode ?? value.value ?? value.name ?? "";
    }
    return "";
}

function setHidden(widget, hidden) {
    if (!widget) return;
    widget.hidden = hidden;
    widget.options ??= {};
    widget.options.hidden = hidden;
}

function refresh(node) {
    const modeWidget = node.widgets?.find((widget) => widget?.name === "mode");
    const seedWidget = node.widgets?.find((widget) => widget?.name === "seed");
    if (!modeWidget || !seedWidget) return;

    const isRandom = getMode(modeWidget) === "Random";
    setHidden(seedWidget, !isRandom);

    // The seed is a stable top-level native ComfyUI widget. Only hide/show
    // its existing linked control. Never create, remove, reorder or mutate it.
    const linkedControls = (seedWidget.linkedWidgets ?? []).filter(
        (widget) => widget?.name === "control_after_generate"
    );

    if (linkedControls.length) {
        for (const control of linkedControls) {
            setHidden(control, !isRandom);
        }
    } else {
        // Compatibility fallback for frontends that do not expose linkedWidgets.
        // There should be one native control; this never creates another one.
        for (const control of node.widgets ?? []) {
            if (control?.name === "control_after_generate") {
                setHidden(control, !isRandom);
            }
        }
    }

    node.graph?.setDirtyCanvas?.(true, true);
}

app.registerExtension({
    name: "Reign-In-Nodes.RandomCharacterVisibility",

    nodeCreated(node) {
        if (node.comfyClass !== NODE_ID) return;

        requestAnimationFrame(() => {
            const modeWidget = node.widgets?.find((widget) => widget?.name === "mode");
            if (!modeWidget) return;

            const originalCallback = modeWidget.callback;
            modeWidget.callback = function (...args) {
                const result = originalCallback?.apply(this, args);
                requestAnimationFrame(() => refresh(node));
                return result;
            };

            refresh(node);
        });
    },
});
