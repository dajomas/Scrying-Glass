import copy
import json
import unittest
from python.scrying_glass_monster_initiative import initiative_patch, normalize_initiative
from python.scrying_glass_monster_refresh import capture_review, prepare_refresh, StaleRefreshError

class InitiativeTests(unittest.TestCase):
    def test_examples(self):
        m = initiative_patch({}, bonus=12)
        for r, t in ((16,28),(10,22),(16,28)):
            m.update(initiative_patch(m, roll=r))
            self.assertEqual(m["initiative"], t)
        self.assertEqual(initiative_patch(m, bonus=10)["initiative"], 26)
    def test_defaults_and_signed(self):
        for b, t in ((-2,14),(0,16),(12,28)):
            self.assertEqual(initiative_patch({}, roll=16, bonus=b)["initiative"], t)
        self.assertEqual(initiative_patch({}, roll=16)["initiative_bonus_origin"], "default")
        self.assertEqual(initiative_patch({}, bonus=0)["initiative_bonus_origin"], "manual")
    def test_legacy(self):
        m = initiative_patch({"initiative":23}, bonus=12, origin="source")
        self.assertEqual(m["initiative"],23)
        self.assertIsNone(m["initiative_roll"])
        self.assertEqual(initiative_patch(m,roll=16)["initiative"],28)
    def test_clear(self):
        self.assertIsNone(initiative_patch({"initiative":23},roll=None)["initiative"])
        self.assertIsNone(initiative_patch({},bonus=12)["initiative"])
    def test_reload(self):
        m = initiative_patch({},roll=16,bonus=12)
        for _ in range(10):
            m = normalize_initiative(json.loads(json.dumps(m)))
            self.assertEqual(m["initiative"],28)
    def test_shared(self):
        self.assertEqual([initiative_patch({},bonus=b,roll=16)["initiative"] for b in (12,3,-2)], [28,19,14])
    def test_invalid(self):
        for value in (True,False,1.5,"12",[],{}):
            for field in ("roll","bonus"):
                with self.assertRaises(ValueError): initiative_patch({},**{field:value})
        with self.assertRaises(ValueError): initiative_patch({},bonus=None)
    def test_origin(self):
        for origin in (None,[],{},"bogus"):
            with self.assertRaises(ValueError): initiative_patch({},bonus=1,origin=origin)
        with self.assertRaises(ValueError): initiative_patch({},origin="source")
        with self.assertRaises(ValueError): initiative_patch({},bonus=1,origin="default")
    def test_no_mutation(self):
        m={"initiative":23,"hp":4,"in_turn":True}
        before=copy.deepcopy(m)
        p=initiative_patch(m,roll=16,bonus=12)
        self.assertEqual(m,before)
        self.assertNotIn("hp",p)

class RefreshTests(unittest.TestCase):
    def setUp(self):
        self.monsters=[{"id":"a","name":"A","initiative":23,"hp":4,"max_hp":20,"ac":10},
                       {"id":"b","name":"B","initiative":None,"hp":9,"max_hp":9,"ac":12}]
        self.offers={"a":{"initiative_bonus":12,"ac":18,"hp":"2d8+4","max_hp":"2d8+4"}}
        self.scope=("campaign","setup",1)
        self.review=capture_review(self.scope,self.monsters[:1],self.offers)
        self.rolls=0
        self.factories=0
    def factory(self,spec):
        self.factories+=1
        if spec!="2d8+4": raise ValueError("bad dice")
        def roll():
            self.rolls+=1
            return 15
        return roll
    def apply(self,fields,**kwargs):
        return prepare_refresh(kwargs.get("review",self.review), kwargs.get("scope",self.scope),
                               kwargs.get("live",self.monsters), fields,self.factory)
    def test_preview_no_mutation_or_roll(self):
        self.assertEqual(self.rolls,0)
        self.assertEqual(self.monsters[0]["hp"],4)
        self.offers["a"]["ac"]=99
        self.assertEqual(self.review["rows"]["a"]["offer"]["ac"],18)
    def test_only_selected_fields_and_monsters(self):
        result=self.apply({"a":["ac"]})
        self.assertEqual(set(result),{"a"})
        self.assertEqual(result["a"]["ac"],18)
        self.assertEqual(result["a"]["hp"],4)
        self.assertEqual(self.monsters[0]["ac"],10)
        self.assertEqual(self.factories,0)
    def test_hp_pair_one_roll(self):
        result=self.apply({"a":["hp","max_hp"]})
        self.assertEqual((result["a"]["hp"],result["a"]["max_hp"]),(15,15))
        self.assertEqual(self.rolls,1)
    def test_max_only_preserves_hp(self):
        result=self.apply({"a":["max_hp"]})
        self.assertEqual((result["a"]["hp"],result["a"]["max_hp"]),(4,15))
    def test_hp_only_preserves_max(self):
        result=self.apply({"a":["hp"]})
        self.assertEqual((result["a"]["hp"],result["a"]["max_hp"]),(15,20))
    def test_legacy_and_normal_bonus_refresh(self):
        self.assertEqual(self.apply({"a":["initiative_bonus"]})["a"]["initiative"],23)
        self.monsters[0].update(initiative_patch(self.monsters[0],roll=16))
        review=capture_review(self.scope,self.monsters[:1],self.offers)
        self.assertEqual(self.apply({"a":["initiative_bonus"]},review=review)["a"]["initiative"],28)
    def test_unselected_id_rejected(self):
        with self.assertRaises(ValueError):self.apply({"b":["ac"]})
    def test_scope_stale(self):
        with self.assertRaises(StaleRefreshError):self.apply({"a":["hp"]},scope=("other","setup",1))
        self.assertEqual(self.rolls,0)
    def test_changed_and_deleted(self):
        live=copy.deepcopy(self.monsters)
        live[0]["hp"]=3
        with self.assertRaises(StaleRefreshError):self.apply({"a":["hp"]},live=live)
        with self.assertRaises(StaleRefreshError):self.apply({"a":["hp"]},live=[])
    def test_missing_fields(self):
        review=capture_review(self.scope,self.monsters[:1],{"a":{"initiative_bonus":None}})
        with self.assertRaises(ValueError):self.apply({"a":["initiative_bonus"]},review=review)
        self.assertEqual(self.monsters[0]["initiative"],23)
    def test_invalid_selection(self):
        for fields in ([],["ac","ac"],["name"],[True],"ac"):
            with self.assertRaises(ValueError):self.apply({"a":fields})
    def test_all_validate_before_dice(self):
        offers=copy.deepcopy(self.offers)
        offers["b"]={"ac":1000}
        review=capture_review(self.scope,self.monsters,offers)
        with self.assertRaises(ValueError):self.apply({"a":["hp"],"b":["ac"]},review=review)
        self.assertEqual(self.rolls,0)
    def test_bad_generated_hp_no_mutation(self):
        before=copy.deepcopy(self.monsters)
        for value in (True,-1,2**63):
            with self.assertRaises(ValueError):
                prepare_refresh(self.review,self.scope,self.monsters,{"a":["hp"]},lambda spec:lambda:value)
        self.assertEqual(self.monsters,before)
