app.registerExtension({
    name: "Reign_Imagereroute",
    nodeCreated(node) {
        if (node.type === "Reign_Imagereroute") {
            node.title = "";
            node.widgets = [];
            node.size = [100, 40];
            node.color = "#6666aa";
            node.bgcolor = "#6666aa";
            node.boxcolor = "#333366"; 
            node.shape = LiteGraph.BOX_SHAPE;
        }
    }
});