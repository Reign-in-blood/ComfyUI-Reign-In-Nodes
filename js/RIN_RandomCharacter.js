import { app } from "../../scripts/app.js";

const NODE_ID = "RIN_RandomCharacter";

function modeValue(widget) {
    const value = widget?.value;
    if (typeof value === "string") return value;
    if (value && typeof value === "object") {
        return value.mode ?? value.value ?? value.name ?? "";
    }
    return "";
}

function setWidgetHidden(widget, hidden) {
    if (!widget) return;
    widget.hidden = hidden;
}

function refreshSeedVisibility(node) {
    const modeWidget = node.widgets?.find((widget) => widget.name === "mode");
    const seedWidget = node.widgets?.find((widget) => widget.name === "seed");
    if (!modeWidget || !seedWidget) return;

    const isRandom = modeValue(modeWidget) === "Random";
    const controlWidget = seedWidget.linkedWidgets?.[0]
        ?? node.widgets?.find((widget) => widget.name === "control_after_generate");

    if (isRandom) {
        setWidgetHidden(seedWidget, false);
        setWidgetHidden(controlWidget, false);

        if (controlWidget && node.__rinRandomSeedControlMode) {
            controlWidget.value = node.__rinRandomSeedControlMode;
        }
    } else {
        if (controlWidget) {
            if (controlWidget.value && controlWidget.value !== "fixed") {
                node.__rinRandomSeedControlMode = controlWidget.value;
            }
            controlWidget.value = "fixed";
        }

        setWidgetHidden(seedWidget, true);
        setWidgetHidden(controlWidget, true);
    }

    const size = node.computeSize?.();
    if (size) node.setSize?.(size);
    node.graph?.setDirtyCanvas?.(true, true);
}

app.registerExtension({
    name: "Reign-In-Nodes.RandomCharacterUI",

    nodeCreated(node) {
        if (node.comfyClass !== NODE_ID) return;

        requestAnimationFrame(() => {
            const modeWidget = node.widgets?.find((widget) => widget.name === "mode");
            if (!modeWidget) return;

            const originalCallback = modeWidget.callback;
            modeWidget.callback = function (...args) {
                const result = originalCallback?.apply(this, args);
                requestAnimationFrame(() => refreshSeedVisibility(node));
                return result;
            };

            refreshSeedVisibility(node);
        });
    },
});
