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

function getSeedControl(node, seedWidget) {
    const linked = seedWidget?.linkedWidgets?.find(
        (widget) => widget?.name === "control_after_generate"
    );
    if (linked) return linked;

    const controls = node.widgets?.filter(
        (widget) => widget?.name === "control_after_generate"
    ) ?? [];

    return controls.length ? controls[controls.length - 1] : null;
}

function removeGhostSeedControls(node, keepWidget) {
    if (!node.widgets) return;

    for (let index = node.widgets.length - 1; index >= 0; index--) {
        const widget = node.widgets[index];
        if (
            widget?.name === "control_after_generate"
            && widget !== keepWidget
        ) {
            widget.onRemove?.();
            node.widgets.splice(index, 1);
        }
    }
}

function refreshSeedVisibility(node) {
    const modeWidget = node.widgets?.find((widget) => widget.name === "mode");
    const seedWidget = node.widgets?.find((widget) => widget.name === "seed");
    if (!modeWidget || !seedWidget) return;

    const controlWidget = getSeedControl(node, seedWidget);
    removeGhostSeedControls(node, controlWidget);

    const isRandom = modeValue(modeWidget) === "Random";

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
