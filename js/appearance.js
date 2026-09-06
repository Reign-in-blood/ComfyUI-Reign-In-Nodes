import { app } from "../../scripts/app.js";

// Thèmes de couleurs réutilisables
const COLOR_THEMES = {
    red:                  { color: "#332222", bgcolor: "#553333" },
    green:                { color: "#223322", bgcolor: "#335533" },
    blue:                 { color: "#222233", bgcolor: "#333355" },
    pale_blue:            { color: "#2a363b", bgcolor: "#3f5159" },
    RIN_blue:             { color: "#1b4669", bgcolor: "#29699c" },
    RIN_Greenmente:       { color: "#A3DE21", bgcolor: "#B5E54D" },
    RIN_Greenmente_inv:   { color: "#B5E54D", bgcolor: "#A3DE21" },
    RIN_Greenlite:        { color: "#74BA45", bgcolor: "#90C86A" },
    RIN_Greenemeraude:    { color: "#38C797", bgcolor: "#5FD3AC" },
    RIN_Greenbrown:       { color: "#C08A3F", bgcolor: "#CDA265" },
    RIN_Greenham:         { color: "#AB6554", bgcolor: "#BC8376" },
    RIN_Greenpinky:       { color: "#FF31D0", bgcolor: "#FF64DC" },
    cyan:                 { color: "#223333", bgcolor: "#335555" },
    purple:               { color: "#332233", bgcolor: "#553355" },
    yellow:               { color: "#443322", bgcolor: "#665533" },
};

// Configuration automatique par comfyClass
const NODE_STYLES = {
    "replace Prompt Text":          { theme: "green", size: [500, 90] },
    "Prompt Text Output Pos":       { theme: "green", size: [500, 250] },
    "Simple String Node":           { theme: "green", size: [500, 150] },
    "Concat Text":                  { theme: "green", size: [500, 150] },

    "Prompt Text Output Neg":       { theme: "red", size: [500, 250] },
    "VAELoader":                    { theme: "red", size: [500, 60] },

    "BusCan Basic":                 { theme: "cyan", size: [200, 130] },
    "BusCan Basic +":               { theme: "cyan", size: [200, 170] },
    "BusCan Any 4":                 { theme: "cyan", size: [200, 110] }, 
    "BusCan Any 6":                 { theme: "cyan", size: [200, 150] }, 
    "BusCan Any 8":                 { theme: "cyan", size: [200, 190] }, 
    "BusCan Any 12":                { theme: "cyan", size: [200, 270] }, 

    "SDXL Size Loader":             { theme: "purple", size: [330, 120] },
    "FLUX Size Loader":             { theme: "purple", size: [330, 120] },
    "CFG Steps":                    { theme: "purple", size: [330, 100] },
    "sampler scheduler":            { theme: "purple", size: [330, 140] },

    "RgthreeSeed":                  { theme: "purple", size: [330, 130] },
    "RgthreeBaseServerNode":        { theme: "purple", size: [330, 130] },
    
    "TSC_KSampler":                 { theme: "purple", size: [330, 560] },
    "TSC_KSamplerAdvanced":         { theme: "purple", size: [330, 560] },


    "VAED encode Preview":          { theme: "RIN_blue" },
    "Nearest SDXL Resolution":      { theme: "RIN_blue" },
    "Plasma Noise Generator":       { theme: "RIN_blue" },
    "Random Noise Generator":       { theme: "RIN_blue" },
    "Rotate Image":                 { theme: "RIN_blue" },
    "Any Switch":                   { theme: "RIN_blue" },
    "Super Image Loader":           { theme: "RIN_blue" },
    
    // Vanilla nodes
    
    "SaveImage":                    { theme: "RIN_blue", size: [300, 400] },
    "PreviewImage":                 { theme: "RIN_blue", size: [300, 400] },
    "KSampler":                     { theme: "purple", size: [330, 260] },
    "EmptyLatentImage":             { theme: "purple", size: [300, 110] },
    "CheckpointLoaderSimple":       { theme: "cyan", size: [500, 100] },
    "LoraLoader":                   { theme: "cyan", size: [500, 110] },
    "CLIPSetLastLayer":             { theme: "yellow", size: [500, 60] },

};

// Extension enregistrée automatiquement


app.registerExtension({
    name: "Reign-In-Nodes.appearance",
    nodeCreated(node) {
        const config = NODE_STYLES[node.comfyClass];
        if (!config) return;

        const theme = COLOR_THEMES[config.theme];
        if (theme) {
            node.color = theme.color;
            node.bgcolor = theme.bgcolor;
        }

        if (config.size) {
            node.setSize(config.size);
        }
    }
});