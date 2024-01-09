if (!window.dash_clientside) {
    window.dash_clientside = {};
}
window.dash_clientside.battle_log = {
    clear_history: function(clicks) {
        if (typeof clicks === 'undefined') { return window.dash_clientside.no_update; }
        return [];
    },

    disable_download: function(data) {
        if (data.length === 0) {
            return true;
        }
        return false;
    },

    toggle_bo1_bo3: function(games) {
        if (games == '1') {
            return ['mt-1', 'd-none', 'd-none'];
        }
        return Array(3).fill('mt-1');
    },

    clear_battle_log_options: function(clicks) {
        if (typeof clicks === 'undefined') { return window.dash_clientside.no_update; }
        return [
            undefined,
            Array(3).fill(undefined),
            Array(3).fill(undefined),
            Array(3).fill([]),
            Array(3).fill('')
        ];
    },

    disabled_submit: function(playing, against, result) {
        if (typeof playing === 'undefined') { return true; }
        if (typeof against === 'undefined') { return true; }
        if (typeof result === 'undefined') { return true; }
        return false;
    },
}