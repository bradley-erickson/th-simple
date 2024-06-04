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
            window.drake.on("drop", function(_el, target, source, sibling) {
                const dropComplete = new CustomEvent('dropcomplete', {
                    bubbles: true,
                    detail: {
                      id: _el.id,
                      target: target.id
                    },
                    target_id: target.id
                  });
                target.dispatchEvent(dropComplete)
            })
        }, 1)
        return window.dash_clientside.no_update
    },
}