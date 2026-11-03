"""Verify the technical split preserves its pinned source and legacy anchors."""
import hashlib
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PARTS = ('010-architecture-runtime-security.md',
         '020-apis-workflows-validation.md', '030-attack-statistics.md')
BEGIN = '<!-- BEGIN preserved technical content -->\n'
END = '<!-- END preserved technical content -->'


def slug(text):
    return re.sub(r'[^\w\- ]', '', text.lower()).replace(' ', '-')


class TechnicalDocumentationSplitTests(unittest.TestCase):
    def test_content_and_size(self):
        source = '# Scrying Glass Technical Documentation\n\n'
        directory = ROOT / 'docs/technical'
        self.assertEqual({p.name for p in directory.iterdir()}, set(PARTS))
        for name in PARTS:
            data = (directory / name).read_bytes()
            self.assertLessEqual(len(data), 20000)
            text = data.decode('utf-8')
            self.assertEqual(text.count(BEGIN), 1)
            self.assertEqual(text.count(END), 1)
            self.assertIn('(../Technical-Documentation.md)', text)
            source += text.split(BEGIN, 1)[1].split(END, 1)[0].replace('](../../Patch/', '](../Patch/')
        raw = source.encode('utf-8')
        self.assertEqual(len(raw), 31226)
        self.assertEqual(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest(),
                         '7f9861b62a11c6efeb82fcb286f5abe300f4db2e')

    def test_compatibility_links(self):
        index = (ROOT / 'docs/Technical-Documentation.md').read_text(encoding='utf-8')
        self.assertLessEqual(len(index.encode('utf-8')), 20000)
        index_anchors = {slug(title) for title in re.findall(r'^#{2,3} (.+)$', index, re.M)}
        links = re.findall(r'\]\(technical/([^#)]+)#([^)]+)\)', index)
        self.assertEqual(len(links), 25)
        for filename, anchor in links:
            self.assertIn(filename, PARTS)
            text = (ROOT / 'docs/technical' / filename).read_text(encoding='utf-8')
            self.assertIn(anchor, {slug(title) for title in re.findall(r'^#{1,3} (.+)$', text, re.M)})
            self.assertIn(anchor, index_anchors)


if __name__ == '__main__':
    unittest.main()
