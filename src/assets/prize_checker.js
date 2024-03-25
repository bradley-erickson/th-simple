if (!window.dash_clientside) {
    window.dash_clientside = {};
}
window.dash_clientside.prize_checker = {

    disable_import: function (val) {
        if (val.length > 0) { return false; }
        return true;
    },

    update_event_listener: function (id) {
        const element = document.querySelector(`#${id}`);
        element.addEventListener('wheel', function(event) {
            event.preventDefault();
        }, true)
        return window.dash_clientside.no_update;
    },

    update_index: function (n, e, idx, children) {
        if (typeof e === 'undefined') { return window.dash_clientside.no_update; }
        const size = children.length
        if (e.wheelDelta < 0) {
            return Math.max(idx - 1, 0)
        } else {
            return Math.min(idx + 1, size - 1)
        }
    },

    advance_card: function(i) {
        const items = document.querySelectorAll('.card-in-stack');
        for (let item of items) { item.classList.remove('target'); }
        items[i].classList.add('target');
        items[i].scrollIntoView({ block: 'nearest', inline: 'nearest', behavior: 'smooth' });
        return '';
    },

    check_status: function(value, prizes) {
        if (value === null) { return ''; }
        const trig = window.dash_clientside.callback_context.triggered_id.index
        const match = prizes.filter(obj => obj.card_code === trig)
        return match.length === value ? 'fas fa-check text-success' : 'fas fa-xmark text-danger'
    }

}
