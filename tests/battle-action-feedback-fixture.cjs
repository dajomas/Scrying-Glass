// Real controller and Admin scope bootstrap, without mounting a feedback view.
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {createController} = require('../static/admin-feedback-controller.js');
const bootstrap = fs.readFileSync(path.join(__dirname, '../static/admin-feedback-admin.js'), 'utf8');
function installFeedback(context, options = {}) {
    context.window ||= {};
    context.document.getElementById = () => null;
    context.ScryingFeedback = {createController: () => createController(options)};
    vm.createContext(context);
    vm.runInContext(bootstrap, context);
    const feedback = context.window.scryingAdminFeedback;
    const scope = (campaign = 'fixture', name = 'setup') => {
        if (!feedback.observeState({active_campaign_id: campaign,
            active_setup: {campaign_id: campaign, name}}, feedback.stateRequest())) {
            throw new Error('Invalid fixture encounter scope');
        }
    };
    scope();
    return {feedback, scope};
}
module.exports = {installFeedback};
