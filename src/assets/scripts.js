if (!window.dash_clientside) {
    window.dash_clientside = {};
}

function cleanStringForId(input) {
    // Remove symbols except for whitespace (to be replaced with underscores)
    // This regex matches any character that is not a letter, number, or whitespace
    const cleanedInput = input.replace(/[^\w\s]/gi, '');

    // Replace whitespace with underscores
    const underscoresForSpaces = cleanedInput.replace(/\s+/g, '-');

    // Convert to lowercase
    const lowercaseOutput = underscoresForSpaces.toLowerCase();

    return lowercaseOutput;
}

window.dash_clientside.clientside = {
    toggle_with_button: function (clicks, is_open) {
        if (clicks > 0) {
            return !is_open;
        }
        return is_open;
    },

    disable_tour_filter_apply: function (players, start, end, platform, game, initial) {
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
        if (game !== initial.game) {
            return false;
        }
        return true;
    },

    update_tour_filter_apply_href: function (players, start, end, platform, game, hash) {
        const end_string = end !== null ? `&end_date=${end}` : '';
        const platform_string = platform !== null ? `&platform=${platform}` : '';
        return `?game=${game}&players=${players}&start_date=${start}${end_string}${platform_string}#${hash}`;
    },

    return_self: function (self) {
        return self;
    },

    update_diff_title: function (text) {
        if (typeof text === 'undefined') { return ''; }
        return text
    },

    update_feedback_submit_disabled: function (arg, contactType, contactUser) {
        const messageCheck = arg.length > 10
        const contactCheck = contactType === 'None' | contactUser.length > 0
        return [
            !messageCheck | !contactCheck,
            messageCheck ? 'd-none' : '',
            contactCheck ? 'd-none' : ''
        ];
    },

    download_dom_as_image: async function (clicks, id, theme) {
        const today = new Date();
        const dateString = today.toISOString().substring(0, 10);
        fileName = `trainerhill-${id}-${dateString}.png`;
        if (clicks > 0) {
            html2canvas(document.getElementById(id), { useCORS: true, backgroundColor: theme ? '#222222' : '#ffffff' }).then(function (canvas) {
                // var newWindow = window.open('', windowFeatures='popup');
                // newWindow.document.title = 'TH - Generated Image'
                // newWindow.document.write('<img src="' + canvas.toDataURL('image/png') + '"/>');
                var anchorTag = document.createElement('a');
                anchorTag.download = fileName;
                anchorTag.href = canvas.toDataURL('image/png');
                anchorTag.target = '_blank';
                document.body.appendChild(anchorTag);
                anchorTag.click();
                document.body.removeChild(anchorTag);
            })
        }
    },

    archetype_builder_disbaled_add: function (icons, name, curr, extra) {
        const id = cleanStringForId(name);
        const exists = name.length === 0 | curr.some(deck => deck.id === id) | extra.includes(id);

        if (icons.length > 0 & !exists) {
            return [false, ''];
        }
        if (icons.length === 0) { return [true, `Please select icons${name.length === 0 ? ' and input name' : ''}.`] }
        if (name.length === 0) { return [true, 'Please input name.'] }
        if (exists) { return [true, 'Name already exists, please try a different name.']; }
        return [true, 'Something is wrong.'];
    },

    archetype_builder_add_deck: function (clicks, icons, name, curr) {
        const id = cleanStringForId(name)
        if (clicks === 0) {
            return window.dash_clientside.no_update;
        }
        const newDeck = { id, name, icons }
        return [curr.concat([newDeck]), [], ''];
    },

    tag_disable_add: function (val, curr, others) {
        const exists = val.length === 0 | curr.some(v => v === val) | others.includes(val);
        return exists;
    },

    clear_tour_report_data: function(clicks) {
        if (typeof clicks === 'undefined') { return window.dash_clientside.no_update; }
        return [{}, {}, 'tour-meta-report-upload-tab', ''];
    },

    show_hide_all_items: function(toggle, currentItems) {
        if (toggle) {
            return Array(currentItems.length).fill('');
        }
        return Array(currentItems.length).fill('d-none');
    },

    toggle_tier_list_meta_share: function(toggle) {
        if (toggle) {
            return ['', ''];
        }
        return ['w-100', 'd-none'];
    }
}
