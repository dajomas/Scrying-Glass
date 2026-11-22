'use strict';
// static/admin.js is one classic script. Tests that run part of it in a VM with a mocked DOM
// take the lines from one marker line up to (not including) another, so the rest of the
// script's top-level code does not run. Each marker must occur exactly once.
const fs = require('node:fs');
const path = require('node:path');

const source = fs.readFileSync(path.join(__dirname, '..', 'static', 'admin.js'), 'utf8');

function lineStart(marker) {
    const first = source.indexOf(marker);
    if (first < 0 || source.indexOf(marker, first + 1) >= 0) throw new Error(`Admin marker must occur once: ${marker}`);
    if (first > 0 && source[first - 1] !== '\n') throw new Error(`Admin marker must start a line: ${marker}`);
    return first;
}

function adminRange(from, to) {
    return source.slice(from ? lineStart(from) : 0, to ? lineStart(to) : source.length);
}

module.exports = {adminSource: source, adminRange};
