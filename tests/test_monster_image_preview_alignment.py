"""SG-TODO-011: field and preview alignment; intercepted HTTP, not live server."""
import unittest


class PreviewAlignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import test_monster_button_layout as rows
        cls.rows = rows.MonsterButtonLayoutTests
        cls.rows.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        cls.rows.tearDownClass.__func__(cls)

    def test_fields_and_preview_boxes_align_loaded_and_empty(self):
        from test_monster_image_previews import PIXEL
        groups = (('monsterColor', 'monsterImage'),
                  ('monsterFile', 'monsterFileQuantity', 'monsterFileColor', 'monsterFileImage'))
        for width in (1440, 375):
            for loaded in (False, True):
                with self.subTest(width=width, loaded=loaded):
                    page, errors, mutations = self.rows.open_page(self, width)
                    page.wait_for_function("document.body.dataset.monsterImagePreviews === 'ready'")
                    for id in ('toggleBattleSetupPane', 'toggleMonsterPane'):
                        button = page.locator('#' + id)
                        if button.get_attribute('aria-expanded') == 'false':
                            button.click()
                    if loaded:
                        for id in ('monsterImage', 'monsterFileImage'):
                            page.locator('#' + id).set_input_files({'name': id + '.png', 'mimeType': 'image/png', 'buffer': PIXEL})
                            page.wait_for_function('(id) => document.querySelector("#" + id + "Preview img").naturalWidth > 0', arg=id)
                    for ids in groups:
                        tops = page.evaluate("""ids => ids.map(id => document.getElementById(id)
                            .closest('label').querySelector('.field-label').getBoundingClientRect().top)""", list(ids))
                        field = page.locator('#' + ids[-1])
                        group = field.locator('xpath=ancestor::fieldset[1]')
                        self.assertEqual(group.locator(':scope > .sg-group-row').evaluate('n => getComputedStyle(n).alignItems'), 'flex-start')
                        preview = page.locator('#' + ids[-1] + 'Preview')
                        box = preview.bounding_box()
                        input_box = field.bounding_box()
                        self.assertIsNotNone(box)
                        self.assertIsNotNone(input_box)
                        if width == 1440:
                            self.assertLessEqual(max(tops) - min(tops), 1)
                            self.assertAlmostEqual(box['y'], input_box['y'], delta=1)
                            self.assertGreaterEqual(box['x'], input_box['x'] + input_box['width'])
                        else:
                            self.assertGreaterEqual(box['y'], input_box['y'] + input_box['height'])
                        self.assertGreaterEqual(box['x'], 0)
                        self.assertLessEqual(box['x'] + box['width'], width + 1)
                        if not loaded:
                            self.assertEqual(preview.locator('img').count(), 0)
                            self.assertIn('No image selected.', preview.inner_text())
                        for id in ids:
                            self.assertTrue(page.locator('#' + id).is_visible())
                    unrelated = page.locator('#characterForm .sg-group-row').first
                    self.assertEqual(unrelated.evaluate('n => getComputedStyle(n).alignItems'), 'end')
                    self.assertEqual(errors, [])
                    self.assertEqual(mutations, [])
                    page.close()


if __name__ == '__main__':
    unittest.main()
