if (!window.dash_clientside) {
    window.dash_clientside = {};
}
window.dash_clientside.prize_checker = {

    disable_import: function (val) {
        if (val.length > 0) { return false; }
        return true;
    },

    update_index: function (n, e, idx, children) {
        const ids = children.length;
        if (typeof e === 'undefined') { return window.dash_clientside.no_update; }
        const size = ids.length
        // const carousel = document.querySelector('.deck-stack');
        // const width = document.querySelector('.card-in-stack').clientWidth;
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
        items[i].scrollIntoView({ behavior: 'smooth' });
        return '';
    },

    check_status: function(value, prizes) {
        if (value === null) { return ''; }
        const trig = window.dash_clientside.callback_context.triggered_id.index
        const match = prizes.filter(obj => obj.id === trig)
        return match.length === value ? 'fas fa-check text-success' : 'fas fa-xmark text-danger'
    }

}
