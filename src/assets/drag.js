if (!window.dash_clientside) {
    window.dash_clientside = {};
}
window.drake = dragula();
window.dash_clientside.drag = {
    make_draggable: function() {
        let args = Array.from(arguments)[0];
        var els = [];
        window.drake.destroy();
        setTimeout(function() {
            for (i = 0; i < args.length; i++){
                els[i] = document.getElementById(JSON.stringify(args[i]));
            }
            window.drake = dragula(els);
        }, 1)
        return window.dash_clientside.no_update
    },
}