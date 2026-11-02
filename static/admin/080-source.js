async function adjustBattleOrderFont(direction) {
    if (battleOrderFontAdjustmentPending) {
        return;
    }

    battleOrderFontAdjustmentPending = true;

    updateBattleOrderFontControls(
        latest?.display?.battle_order_font_size,
    );

    try {
        const result = await request(
            '/api/display/battle-order-font',
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ direction }),
            },
        );

        if (latest?.display) {
            latest.display.battle_order_font_size = (
                result.battle_order_font_size
            );
        }

        updateBattleOrderFontControls(
            result.battle_order_font_size,
        );
    } catch (error) {
        message(
            error instanceof Error
                ? error.message
                : 'Unable to change viewer font size.',
        );
    } finally {
        battleOrderFontAdjustmentPending = false;

        updateBattleOrderFontControls(
            latest?.display?.battle_order_font_size,
        );
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
