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

    disable_tour_filter_apply: function (players, start, end, platform, initial) {
        if (players !== initial.players) {
            return false;
        }
        if (start !== initial.start_date) {
            return false;
        }
        if (end !== initial.end_date) {
            return false;
        }
        if (platform !== initial.platform) {
            return false;
        }
        return true;
    },

    update_tour_filter_apply_href: function (players, start, end, platform, hash) {
        const end_string = end !== null ? `&end_date=${end}` : '';
        const platform_string = platform !== null ? `&platform=${platform}`: '';
        return `?players=${players}&start_date=${start}${end_string}${platform_string}#${hash}`;
    },

    return_self: function(self) {
        return self;
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
            return [false, 'd-none'];
        }
        return [true, ''];
    },

    download_dom_as_image: async function(clicks, id) {
        const today = new Date();
        const dateString = today.toISOString().substring(0, 10);
        fileName = `trainerhill-${id}-${dateString}.png`;
        if(clicks > 0){
            html2canvas(document.getElementById(id), {useCORS: true}).then(function (canvas) {
                var anchorTag = document.createElement('a');
                document.body.appendChild(anchorTag);
                anchorTag.download = fileName;
                anchorTag.href = canvas.toDataURL();
                anchorTag.target = '_blank';
                anchorTag.click();
            })
        }
    }
}