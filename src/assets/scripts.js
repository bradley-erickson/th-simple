if (!window.dash_clientside) {
    window.dash_clientside = {};
}
window.dash_clientside.clientside = {
    toggle_with_button: function(clicks, is_open) {
        if (clicks > 0) {
            return !is_open;
        }
        return is_open;
    },

    disable_tour_filter_apply: function (players, start, end, initial) {
        if (players !== initial.players) {
            return false;
        }
        if (start !== initial.start_date) {
            return false;
        }
        if (end !== initial.end_date) {
            return false;
        }
        return true;
    },

    update_tour_filter_apply_href: function (players, start, end, hash) {
        const end_string = end !== null ? `&end_date=${end}` : '';
        return `?players=${players}&start_date=${start}${end_string}#${hash}`;
    },

    update_text: function(text) {
        return text;
    },

    update_diff_title: function(text) {
        if (typeof text === 'undefined') { return ''; }
        if (text.length > 0) {
            return ` - ${text}`;
        }
        return '';
    },

    update_feedback_submit_disabled: function(arg) {
        if (arg.length > 10) {
            return false;
        }
        return true;
    }
}