import unittest
from python.scrying_glass_feature_rules import apply_hp
from python.scrying_glass_health_limits import MAX_STORED_HP

class HealingCapTests(unittest.TestCase):
    def item(self, hp=18, max_hp=20, **extra):
        return dict(hp=hp, max_hp=max_hp, active=True, alive=hp>0,
                    life_state='standing' if hp else 'down', **extra)

    def test_excess_healing_caps(self):
        item=self.item(); apply_hp(item, 10); self.assertEqual(item['hp'],20)

    def test_partial_healing(self):
        item=self.item(hp=5); apply_hp(item, 3); self.assertEqual(item['hp'],8)

    def test_full_hp_stays_full(self):
        item=self.item(hp=20); apply_hp(item, 10); self.assertEqual(item['hp'],20)

    def test_temporary_hp_unchanged(self):
        item=self.item(temp_hp=7); apply_hp(item,10)
        self.assertEqual((item['hp'],item['temp_hp']),(20,7))

    def test_damage_then_healing(self):
        item=self.item(hp=10,temp_hp=3); apply_hp(item,-8); apply_hp(item,999)
        self.assertEqual((item['hp'],item['temp_hp']),(20,0))

    def test_downed_character_recovers(self):
        item=self.item(hp=0,death_failures=2); apply_hp(item,100)
        self.assertEqual((item['hp'],item['life_state'],item['death_failures']),(20,'standing',0))

    def test_dead_character_not_revived(self):
        item=self.item(hp=0); item['life_state']='dead'; apply_hp(item,100)
        self.assertEqual((item['hp'],item['life_state']),(0,'dead'))

    def test_zero_max_hp_does_not_revive(self):
        item=self.item(hp=0,max_hp=0,death_failures=1); apply_hp(item,10)
        self.assertEqual((item['hp'],item['life_state'],item['death_failures']),(0,'down',1))

    def test_storage_limit_healing_is_capped(self):
        item=self.item(hp=MAX_STORED_HP,max_hp=MAX_STORED_HP)
        apply_hp(item,99999); self.assertEqual(item['hp'],MAX_STORED_HP)

    def test_monster_healing_caps(self):
        item=self.item(monster_species='Goblin'); apply_hp(item,100)
        self.assertEqual(item['hp'],20)

    def test_existing_over_max_hp_corrected_on_healing(self):
        item=self.item(hp=30); apply_hp(item,1); self.assertEqual(item['hp'],20)

    def test_zero_change_does_not_heal(self):
        item=self.item(hp=0,death_failures=1); apply_hp(item,0)
        self.assertEqual((item['hp'],item['death_failures']),(0,1))

if __name__=='__main__': unittest.main()
