"""Static and native-DOM checks for the manual creation bonus field."""
import ast
import hashlib
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates/admin/060_monster_input.html"


class FormInputs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.form = None
        self.inputs = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if "id" in values:
            self.ids.add(values["id"])
        if tag == "form":
            self.form = values.get("id")
        if tag == "input":
            self.inputs.append((self.form, values))

    def handle_endtag(self, tag):
        if tag == "form":
            self.form = None


class StaticFormTests(unittest.TestCase):
    def test_optional_signed_field_and_help(self):
        parser = FormInputs()
        parser.feed(TEMPLATE.read_text(encoding="utf-8"))
        fields = [(form, values) for form, values in parser.inputs if values.get("name") == "initiative_bonus"]
        self.assertEqual(len(fields), 1)
        form, field = fields[0]
        self.assertEqual(form, "monsterForm")
        self.assertEqual(field["id"], "monsterInitiativeBonus")
        self.assertEqual(field["type"], "number")
        self.assertEqual(field["step"], "1")
        self.assertEqual(field["placeholder"], "0")
        self.assertNotIn("required", field)
        self.assertNotIn("min", field)
        self.assertNotIn("max", field)
        self.assertEqual(field.get("value", ""), "")
        self.assertEqual(field["aria-describedby"], "monsterInitiativeBonusHelp")
        self.assertIn(field["aria-describedby"], parser.ids)

    def test_bonus_parameter_is_optional_form_input(self):
        tree = ast.parse((ROOT / "python/scrying_glass_monster_selection.py").read_text(encoding="utf-8"))
        cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "CandidateMonstersMixin")
        method = next(node for node in cls.body if getattr(node, "name", "") == "create_monster")
        args = method.args.args
        position = next(i for i, arg in enumerate(args) if arg.arg == "initiative_bonus")
        default = method.args.defaults[position - (len(args)-len(method.args.defaults))]
        self.assertIsInstance(default, ast.Call)
        self.assertEqual(default.func.id, "Form")
        self.assertEqual(default.args[0].value, "")
        self.assertEqual(args[position].annotation.id, "str")

    def test_existing_import_form_is_unchanged(self):
        fragment = TEMPLATE.read_text(encoding="utf-8").split('<form id="monsterUpload"',1)[1].split('</form>',1)[0]
        self.assertEqual(hashlib.sha256(fragment.encode()).hexdigest(), "7dcc0bda1e369d9b037095d02e60d97fd64cf0ade494299724e68015e76ff423")


class NativeFormDataTests(unittest.TestCase):
    def test_native_values_reset_and_scope(self):
        from playwright.sync_api import sync_playwright
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                page = browser.new_page(viewport={"width":375,"height":900})
                page.set_content(TEMPLATE.read_text(encoding="utf-8"))
                for value in ("", "12", "-2", "0"):
                    page.eval_on_selector("#monsterInitiativeBonus", "(field,value) => field.value=value", value)
                    submitted = page.eval_on_selector("#monsterForm", "form => new FormData(form).get('initiative_bonus')")
                    self.assertEqual(submitted, value)
                self.assertFalse(page.eval_on_selector("#monsterUpload", "form => new FormData(form).has('initiative_bonus')"))
                page.eval_on_selector("#monsterInitiativeBonus", "field => field.value='12'")
                page.eval_on_selector("#monsterForm", "form => form.reset()")
                self.assertEqual(page.input_value("#monsterInitiativeBonus"), "")
            finally:
                browser.close()
