import { app } from "../../scripts/app.js";

app.registerExtension({

    name: "RIN_SquareMode",
    async setup() {
        const ctx = CanvasRenderingContext2D.prototype;
        ctx.roundRect = ctx.rect;
        ctx.arc = function(x, y, radius) {
            this.rect(x - radius, y - radius, radius * 2, radius * 2);
        };

        // Add Custom Colors
        if (window.LiteGraph && LiteGraph.LGraphCanvas) {
            LiteGraph.LGraphCanvas.node_colors.RIN_Blue = { color: "#1b4669", bgcolor: "#29699c", groupcolor: "#1b4669" },
            LiteGraph.LGraphCanvas.node_colors.RIN_PaleBlue = { color: "#0a5064", bgcolor: "#1e6478", groupcolor: "#1e6478" },
            LiteGraph.LGraphCanvas.node_colors.RIN_AquaBlue = { color: "#015959", bgcolor: "#008080", groupcolor: "#008080" }
            LiteGraph.LGraphCanvas.node_colors.RIN_GreenMente = { color: "B5E54D", bgcolor: "#A3DE21", groupcolor: "B5E54D" }
            LiteGraph.LGraphCanvas.node_colors.RIN_GreenEmeraude = { color: "#38C797", bgcolor: "#5FD3AC", groupcolor: "#38C797" }
            LiteGraph.LGraphCanvas.node_colors.RIN_GreenLite = { color: "#74BA45", bgcolor: "#90C86A", groupcolor: "#74BA45" }
            LiteGraph.LGraphCanvas.node_colors.RIN_Brown = { color: "#C08A3F", bgcolor: "#CDA265", groupcolor: "#C08A3F" }
            LiteGraph.LGraphCanvas.node_colors.RIN_Ham = { color: "#AB6554", bgcolor: "#BC8376", groupcolor: "#AB6554" }
            LiteGraph.LGraphCanvas.node_colors.RIN_Pinky = { color: "#FF31D0", bgcolor: "#FF64DC", groupcolor: "#FF31D0" }
        ;}
    },
    nodeCreated(node) {
        node.shape = 1;
    }
});