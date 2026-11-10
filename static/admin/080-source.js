async function adjustBattleOrderFont(direction) {
    if (battleOrderFontAdjustmentPending) return;
    const feedback = window.scryingAdminFeedback;
    const ticket = feedback.begin({region: 'global', operation: 'display.battle-order-font',
        target: 'battle-order', label: 'Change viewer font size'});
    battleOrderFontAdjustmentPending = true;

    try {
        updateBattleOrderFontControls(latest?.display?.battle_order_font_size);
        let result;
        try {
            result = await request('/api/display/battle-order-font', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({direction}),
            });
        } catch (error) {
            feedback.publish(ticket, {severity: 'error', text: error instanceof Error
                ? error.message : 'Unable to change viewer font size.'});
            return;
        }
        if (!feedback.isCurrent(ticket)) return;
        // Request succeeded: resolve only its error; UI failures are not POST failures.
        feedback.resolve(ticket);
        if (latest?.display) latest.display.battle_order_font_size = result.battle_order_font_size;
        updateBattleOrderFontControls(result.battle_order_font_size);
    } finally {
        battleOrderFontAdjustmentPending = false;
        updateBattleOrderFontControls(latest?.display?.battle_order_font_size);
    }
}

document.querySelector(
    '#battleOrderFontDecrease',
).addEventListener('click', () => {
    adjustBattleOrderFont('decrease');
});

document.querySelector(
    '#battleOrderFontIncrease',
).addEventListener('click', () => {
    adjustBattleOrderFont('increase');
});

installColorPreview('#monsterColor', '#monsterColorPreview');
installColorPreview('#monsterFileColor', '#monsterFileColorPreview',);
installColorPreview('#characterColor', '#characterColorPreview',);
installColorPreview('#backgroundColor', '#backgroundColorPreview',);

load();
setups();
