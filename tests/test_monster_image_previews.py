"""SG-TODO-011: intercepted HTTP and real Chromium, not live providers."""
import base64
import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PIXEL = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aZ1kAAAAASUVORK5CYII=')


class PreviewSourceTests(unittest.TestCase):
    def test_asset_order_and_sizes(self):
        head = (ROOT / 'templates/admin/000_document_start.html').read_text()
        end = (ROOT / 'templates/admin/190_document_end.html').read_text()
        self.assertEqual(head.count('/static/monster-image-previews.css?v=1'), 1)
        self.assertLess(head.index('/static/admin-panel-forms.css'), head.index('/static/monster-image-previews.css'))
        self.assertEqual(end.count('/static/monster-image-previews.js?v=1'), 1)
        self.assertLess(end.index('/static/admin-panel-forms.js'), end.index('/static/monster-image-previews.js'))
        self.assertIn('<script src="/static/monster-image-previews.js?v=1" defer></script>', end)
        for name in ('monster-image-previews.js', 'monster-image-previews.css', 'monster-candidate-selection.js'):
            self.assertLessEqual((ROOT / 'static' / name).stat().st_size, 20000)


class ProviderPreviewTests(unittest.TestCase):
    def setUp(self):
        from test_monster_candidate_browser import CandidateBrowserTests
        CandidateBrowserTests.setUp(self)
        self.page.evaluate("""() => {
            const label = document.createElement('label'); label.className='field';
            label.innerHTML='Image<input type="file" id="monsterImage" name="image">';
            document.querySelector('#monsterForm').append(label);
            const form=document.createElement('form'); form.id='monsterUpload';
            form.innerHTML='<label class="field">Replace image<input type="file" id="monsterFileImage" name="image"></label>';
            document.body.append(form);
            window.revoked=[]; const revoke=URL.revokeObjectURL.bind(URL);
            URL.revokeObjectURL=url => { revoked.push(url); revoke(url); };
        }""")
        self.page.route('https://images.test/**', lambda r: r.fulfill(content_type='image/png', body=PIXEL))
        self.page.add_script_tag(content=(ROOT / 'static/monster-image-previews.js').read_text())

    def candidate(self, provider='D&D Beyond', image='https://images.test/a.png'):
        return dict(found=True, name='Goblin', species='Goblin', provider=provider, source='MM', legacy=False,
                    ac=12, hp='7', image_url=image, selection_token='image-token')

    def begin(self, candidates):
        self.result={'status':'ok', 'candidates':candidates}
        self.page.evaluate("""
            window.previewLookupSettled = false;
            window.done = lookupMonsterSpeciesStats().finally(() => {
                window.previewLookupSettled = true;
            });
            void 0;
        """)

    def finish(self):
        self.page.wait_for_function("""
            () => window.previewLookupSettled ||
                document.querySelector(
                    'dialog[aria-label="Review monster initiative bonus"][open]'
                ) !== null
        """, timeout=5000)
        review = self.page.get_by_role(
            'dialog', name='Review monster initiative bonus', exact=True)
        if review.count():
            review.get_by_role(
                'button',
                name='Keep current bonus and use candidate',
                exact=True,
            ).click()
        self.page.wait_for_function(
            '() => window.previewLookupSettled === true',
            timeout=5000,
        )
        self.page.evaluate('window.done')

    def file(self, id, name):
        self.page.locator('#'+id).set_input_files({'name':name, 'mimeType':'image/png', 'buffer':PIXEL})

    def test_both_providers_local_precedence_separate_replacement_and_reset(self):
        for provider in ('D&D Beyond', '5e.tools'):
            self.begin([self.candidate(provider)])
            self.finish()
            self.page.wait_for_function("document.querySelector('#monsterImagePreview img').naturalWidth > 0")
            self.assertIn(provider, self.page.locator('#monsterImagePreview').inner_text())
            self.assertEqual(self.page.evaluate("new FormData(document.querySelector('#monsterForm')).get('selection_token')"), 'image-token')
        self.file('monsterImage', 'first.png')
        first=self.page.locator('#monsterImagePreview img').get_attribute('src')
        self.file('monsterImage', 'second.png')
        self.assertIn(first, self.page.evaluate('revoked'))
        self.file('monsterFileImage', 'replace.png')
        self.begin([self.candidate(image='https://images.test/new.png')])
        self.finish()
        self.assertTrue(self.page.locator('#monsterImagePreview img').get_attribute('src').startswith('blob:'))
        self.assertIn('replace.png', self.page.locator('#monsterFileImagePreview').inner_text())
        self.page.locator('#monsterImage').set_input_files([])
        self.assertEqual(self.page.locator('#monsterImagePreview img').get_attribute('src'), 'https://images.test/new.png')
        for form,id in (('monsterUpload','monsterFileImage'), ('monsterForm','monsterImage')):
            self.page.evaluate('(id) => document.getElementById(id).reset()', form)
            self.assertEqual(self.page.locator('#'+id+'Preview img').count(), 0)
        self.assertEqual(self.errors, [])

    def test_popup_choice_late_file_cancel_stale_and_no_image(self):
        self.begin([self.candidate(), self.candidate('5e.tools','https://images.test/b.png')])
        self.page.get_by_role('dialog').wait_for()
        self.page.get_by_role('button', name='2. Goblin', exact=False).click()
        self.finish()
        self.assertEqual(self.page.locator('#monsterImagePreview img').get_attribute('src'), 'https://images.test/b.png')
        self.begin([self.candidate(), self.candidate('5e.tools')])
        self.page.get_by_role('dialog').wait_for()
        self.page.evaluate("""() => {
            const data=new DataTransfer(); data.items.add(new File(['fixture'],'newer.png',{type:'image/png'}));
            const input=document.querySelector('#monsterImage'); input.files=data.files;
            input.dispatchEvent(new Event('change',{bubbles:true}));
        }""")
        self.page.get_by_role('button', name='1. Goblin', exact=False).click()
        self.finish()
        self.assertTrue(self.page.locator('#monsterImagePreview img').get_attribute('src').startswith('blob:'))
        self.page.locator('#monsterImage').set_input_files([])
        self.begin([self.candidate(), self.candidate('5e.tools')])
        self.page.get_by_role('dialog').wait_for()
        self.page.keyboard.press('Escape')
        self.finish()
        self.assertEqual(self.page.locator('#monsterImagePreview img').count(), 0)
        self.begin([self.candidate(), self.candidate('5e.tools')])
        self.page.get_by_role('dialog').wait_for()
        self.page.evaluate("document.querySelector('#monsterSpecies').value='Orc'; document.querySelector('#monsterSpecies').dispatchEvent(new Event('input',{bubbles:true}))")
        self.finish()
        self.assertEqual(self.page.locator('#monsterImagePreview img').count(), 0)
        self.page.locator('#monsterSpecies').fill('Goblin')
        self.begin([self.candidate(image=None)])
        self.finish()
        self.assertIn('No image available', self.page.locator('#monsterImagePreview').inner_text())
        self.assertEqual(self.errors, [])

    def test_load_failure_safe_url_and_idempotence(self):
        self.page.route('https://images.test/broken.png', lambda r: r.fulfill(status=404))
        self.begin([self.candidate(image='https://images.test/broken.png')])
        self.finish()
        self.page.wait_for_function("document.querySelector('#monsterImagePreview figcaption').textContent.includes('unavailable')")
        self.assertEqual(self.page.evaluate("new FormData(document.querySelector('#monsterForm')).get('selection_token')"), 'image-token')
        self.begin([self.candidate(image='javascript:alert(1)')])
        self.finish()
        self.assertEqual(self.page.locator('#monsterImagePreview img').count(), 0)
        self.page.add_script_tag(content=(ROOT / 'static/monster-image-previews.js').read_text())
        self.assertEqual(self.page.locator('#monsterImagePreview').count(), 1)
        self.assertEqual(self.errors, [])


class FullAdminPreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import test_monster_button_layout as rows
        cls.rows=rows.MonsterButtonLayoutTests
        cls.rows.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        cls.rows.tearDownClass.__func__(cls)

    def test_boot_layout_failed_submission_and_screenshots(self):
        directory=Path(os.environ.get('SG_VISUAL_ARTIFACTS', str(Path(tempfile.gettempdir())/'sg-admin-foundations')))
        directory.mkdir(parents=True, exist_ok=True)
        for width in (1440,375):
            with self.subTest(width=width):
                page,errors,mutations=self.rows.open_page(self,width)
                page.wait_for_function("document.body.dataset.monsterImagePreviews === 'ready'")
                for id in ('toggleBattleSetupPane','toggleMonsterPane'):
                    if page.locator('#'+id).get_attribute('aria-expanded')=='false':
                        page.locator('#'+id).click()
                self.assertEqual(page.locator('#monsterForm legend').all_text_contents(), ['Monster identity','Combat statistics','Appearance'])
                self.assertTrue(page.locator('#monsterImage').evaluate("n => n.form.id === 'monsterForm' && n.closest('fieldset').querySelector('legend').textContent === 'Appearance'"))
                for id in ('monsterImage','monsterFileImage'):
                    page.locator('#'+id).set_input_files({'name':id+'.png','mimeType':'image/png','buffer':PIXEL})
                    page.wait_for_function('(id) => document.querySelector("#"+id+"Preview img").naturalWidth > 0', arg=id)
                    box=page.locator('#'+id+'Preview').bounding_box()
                    field=page.locator('#'+id).bounding_box()
                    self.assertGreaterEqual(box['x'],0)
                    self.assertLessEqual(box['x']+box['width'],width)
                    if width==1440:
                        self.assertGreaterEqual(box['x'],field['x']+field['width'])
                page.route('**/api/monsters', lambda r: r.fulfill(status=400,json={'detail':'Fixture rejection'}))
                for id,value in (('monsterName','Draft'),('monsterAc','12'),('monsterHpRangeStart','7')):
                    page.locator('#'+id).fill(value)
                page.evaluate("document.querySelector('#monsterSpecies').value='goblin'")
                with page.expect_response(lambda r:r.url.endswith('/api/monsters')):
                    page.locator('#monsterForm .sg-form-actions button').click()
                page.wait_for_function("document.querySelector('#monsterAddNotification').textContent.includes('Fixture rejection')")
                self.assertEqual(page.locator('#monsterImage').evaluate('n => n.files[0].name'),'monsterImage.png')
                self.assertTrue(page.locator('#monsterImagePreview img').get_attribute('src').startswith('blob:'))
                page.locator('#monsterInputPane').scroll_into_view_if_needed()
                page.screenshot(path=str(directory/f'011-{width}-image-previews.png'))
                self.assertEqual(page.locator('#monsters td button').count(),11)
                self.assertEqual(errors,[])
                self.assertEqual(mutations,[])
                page.close()


if __name__ == '__main__':
    unittest.main()
