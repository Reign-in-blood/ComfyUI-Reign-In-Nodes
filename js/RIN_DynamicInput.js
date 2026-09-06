/**
 * File: RIN_DynamicInput.js
 * Adapted for RIN_AnySwitch (dynamic any-type inputs)
 */

import { app } from "../../scripts/app.js"

const TypeSlot = { Input: 1, Output: 2 };
const TypeSlotEvent = { Connect: true, Disconnect: false };

// Doit correspondre EXACTEMENT au nom de la classe Python exposée dans NODE_CLASS_MAPPINGS
const _ID = "Any Switch";

// Préfixe des entrées dynamiques
const _PREFIX = "source";

// Type générique côté UI : "*" == any type
const _TYPE = "*";

app.registerExtension({
    name: 'rin_anyswitch.dynamic',
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== _ID) return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const me = onNodeCreated?.apply(this);
            // Démarre avec une entrée dynamique vide
            this.addInput(_PREFIX, _TYPE);
            const slot = this.inputs[this.inputs.length - 1];
            if (slot) slot.color_off = "#666";
            return me;
        };

        const onConnectionsChange = nodeType.prototype.onConnectionsChange;
        nodeType.prototype.onConnectionsChange = function (slotType, slot_idx, event, link_info, node_slot) {
            const me = onConnectionsChange?.apply(this, arguments);

            if (slotType === TypeSlot.Input) {
                if (link_info && event === TypeSlotEvent.Connect) {
                    // Aligne le type de l’input sur le type de la sortie connectée
                    const fromNode = this.graph._nodes.find(n => n.id == link_info.origin_id);
                    if (fromNode) {
                        const parent_link = fromNode.outputs[link_info.origin_slot];
                        if (parent_link) {
                            node_slot.type = parent_link.type || _TYPE;
                            node_slot.name = `${_PREFIX}_`; // sera renuméroté plus bas
                        }
                    }
                } else if (event === TypeSlotEvent.Disconnect) {
                    // Supprime le slot déconnecté
                    try { this.removeInput(slot_idx); } catch {}
                }

                // Renumérotation propre : source_1, source_2, ...
                let idx = 0;
                const slot_tracker = {};
                for (let i = 0; i < this.inputs.length; i++) {
                    const slot = this.inputs[i];

                    // Si un slot est totalement orphelin (rare), on le retire
                    if (slot.link === null && slot.name !== _PREFIX) {
                        try { this.removeInput(i); i--; } catch {}
                        continue;
                    }

                    // Base name avant underscore
                    const name = (slot.name || _PREFIX).split('_')[0] || _PREFIX;

                    // Incrémente le compteur pour ce nom
                    slot_tracker[name] = (slot_tracker[name] || 0) + 1;
                    const count = slot_tracker[name];

                    // Met à jour le label
                    slot.name = `${name}_${count}`;
                    idx++;
                }

                // S'assure qu'il existe toujours un dernier slot vide prêt à recevoir une connexion
                let last = this.inputs[this.inputs.length - 1];
                if (!last || !(last.name === _PREFIX || last.name.startsWith(_PREFIX + "_")) || last.link !== null) {
                    this.addInput(_PREFIX, _TYPE);
                    last = this.inputs[this.inputs.length - 1];
                    if (last) last.color_off = "#666";
                }

                this?.graph?.setDirtyCanvas(true);
                return me;
            }
        };

        return nodeType;
    },
});
