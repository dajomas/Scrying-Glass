/* After a server restart the in-memory sign-in is gone. When an Admin API call
 * answers 401, confirm with /api/state and then go to the sign-in page instead
 * of repeating errors. Other 401 answers keep their normal error handling. */
(() => {
    'use strict';
    if (window.scryingSessionExpiryInstalled) return;
    window.scryingSessionExpiryInstalled = true;
    const original = window.fetch.bind(window);
    let checking = null, leaving = false;
    const isApi = input => {
        try {
            const url = new URL(typeof input === 'string' ? input : input.url, location.href);
            return url.origin === location.origin && url.pathname.startsWith('/api/');
        } catch (error) { return false; }
    };
    async function confirmSignedOut() {
        try {
            const response = await original('/api/state', {cache: 'no-store', credentials: 'same-origin'});
            return response.status === 401;
        } catch (error) { return false; }
    }
    window.fetch = async (input, init) => {
        const response = await original(input, init);
        if (response.status === 401 && !leaving && isApi(input)) {
            checking = checking || confirmSignedOut().finally(() => { checking = null; });
            if (await checking && !leaving) {
                leaving = true;
                location.assign('/login');
            }
        }
        return response;
    };
})();
