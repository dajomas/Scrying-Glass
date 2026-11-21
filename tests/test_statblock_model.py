"""022.02a model-only tests; no application/server or storage initialization."""
import copy
import json
import unittest
from dataclasses import replace

from python.scrying_glass_statblock_model import (
    ModelLimits, StatblockError, canonical_bytes, content_digest, validate_snapshot,
)


def node(ident, kind='paragraph', parent=None, owner=None, position=0, **kwargs):
    return dict(local_id=ident, kind=kind, parent_local_id=parent,
                definition_id=owner, position=position, **kwargs)


def sample():
    return dict(model_version=1, source_label='Vampire', subtitle='Undead',
        completeness='available', definitions=[], facts=[], warnings=[],
        provenance=[dict(position=0, role='selected', provider='file', entity_id='sample',
                         adapter_version='1', credits=[])],
        nodes=[node('p'), node('t', 'text', 'p', text='The '),
               node('species', 'species_placeholder', 'p', position=1),
               node('t2', 'text', 'p', position=2, text=' attacks.')])


class StatblockModelTests(unittest.TestCase):
    def setUp(self):
        self.value = sample()

    def invalid(self, code, value=None, limits=None):
        with self.assertRaises(StatblockError) as cm:
            validate_snapshot(self.value if value is None else value, limits)
        self.assertEqual(cm.exception.code, code)
        self.assertTrue(cm.exception.path)

    def test_valid_roundtrip_and_independence(self):
        v = validate_snapshot(self.value)
        self.assertEqual(v, self.value)
        v['nodes'][1]['text'] = 'Changed'
        self.assertEqual(self.value['nodes'][1]['text'], 'The ')
        self.assertEqual(json.loads(canonical_bytes(self.value))['model_version'], 1)

    def test_limits_reject_invalid_values_and_keys(self):
        for value in (True, False, 0, -1, 1.5, '16', None, 2**63):
            with self.subTest(value=value), self.assertRaises(StatblockError):
                ModelLimits(content_depth=value)
        for mapping in (None, [], {'unknown': 1}):
            with self.subTest(mapping=mapping), self.assertRaises(StatblockError):
                ModelLimits.from_mapping(mapping)
        self.assertEqual(ModelLimits.from_mapping({'content_depth': 32}).content_depth, 32)

    def test_live_fields_and_unknown_headers_rejected(self):
        for key in ('name','species','ac','hp','max_hp','initiative_bonus','html'):
            with self.subTest(key=key):
                v = sample(); v[key] = 1
                self.invalid('invalid_fields', v)

    def test_model_version_is_strict(self):
        for version in (True, 0, 2, '1', None):
            with self.subTest(version=version):
                self.value['model_version'] = version
                self.invalid('unsupported_version')

    def test_array_shapes(self):
        for key in ('facts', 'definitions', 'nodes', 'warnings', 'provenance'):
            v = sample(); v[key] = {}
            self.invalid('invalid_array', v)

    def test_python_cycle_and_non_json_types(self):
        v = sample(); v['nodes'].append(v)
        self.invalid('object_cycle', v)
        for value in (float('nan'), float('inf'), 1.2, b'bytes', set(), (1,)):
            v = sample(); v['subtitle'] = value
            self.invalid('invalid_scalar', v)

    def test_unicode_validation(self):
        for value in ('a\x00b', '\ud800'):
            v = sample(); v['subtitle'] = value
            self.invalid('invalid_text' if '\x00' in value else 'invalid_unicode', v)

    def test_utf8_text_boundary(self):
        limits = ModelLimits(text_value_bytes=128)
        self.value['nodes'] = [node('p'), node('t', 'text', 'p', text='é' * 64)]
        validate_snapshot(self.value, limits)
        self.value['nodes'][1]['text'] += 'é'
        self.invalid('text_limit', limits=limits)

    def test_inline_split_does_not_bypass_text_limit(self):
        self.value['nodes'] = [node('p'), node('a', 'text', 'p', text='a'*70),
            node('b', 'strong', 'p', position=1), node('c', 'text', 'b', text='b'*70)]
        self.invalid('text_limit', limits=ModelLimits(text_value_bytes=128))

    def test_snapshot_exact_boundary(self):
        size = len(json.dumps(self.value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())
        validate_snapshot(self.value, ModelLimits(snapshot_bytes=size))
        self.invalid('snapshot_limit', limits=ModelLimits(snapshot_bytes=size-1))

    def test_node_count_boundary(self):
        validate_snapshot(self.value, ModelLimits(content_nodes=4))
        self.invalid('node_limit', limits=ModelLimits(content_nodes=3))

    def test_depth_boundary_and_configuration(self):
        self.value['nodes'] = [node('p')] + [node(str(i), 'emphasis', 'p' if i==0 else str(i-1)) for i in range(15)]
        validate_snapshot(self.value)
        self.value['nodes'].append(node('last', 'text', '14', text='x'))
        self.invalid('depth_limit')
        validate_snapshot(self.value, ModelLimits(content_depth=17))

    def test_content_cycle(self):
        self.value['nodes'] = [node('a', 'emphasis', 'b'), node('b', 'emphasis', 'a')]
        self.invalid('content_cycle')

    def test_missing_parent(self):
        self.value['nodes'][0]['parent_local_id'] = 'missing'
        self.invalid('unknown_parent')

    def test_duplicate_nodes_and_positions(self):
        self.value['nodes'].append(copy.deepcopy(self.value['nodes'][0]))
        self.invalid('duplicate_node')
        self.value = sample(); self.value['nodes'][2]['position'] = 0
        self.invalid('duplicate_position')

    def test_child_and_root_types(self):
        self.value['nodes'] = [node('text', 'text', text='x')]
        self.invalid('invalid_root')
        self.value['nodes'] = [node('p'), node('bad', 'list_item', 'p')]
        self.invalid('invalid_child')

    def test_integer_and_boolean_fields(self):
        for val in (True, -1, 2**63):
            v = sample(); v['nodes'][0]['position'] = val
            self.invalid('invalid_integer', v)
        self.value['nodes'][0]['enabled'] = 1
        self.invalid('invalid_boolean')

    def add_definition(self, ident='spell'):
        self.value['definitions'].append(dict(local_id=ident, kind='spell', name='Command',
            source_key='spell|Command|XPHB', position=0, source_code='XPHB'))

    def test_definition_limit(self):
        self.add_definition()
        validate_snapshot(self.value, ModelLimits(supporting_definitions=1))
        self.value['definitions'].append(dict(local_id='two',kind='condition',name='Charmed',source_key='condition|Charmed|XPHB',position=1))
        self.invalid('definition_limit', limits=ModelLimits(supporting_definitions=1))

    def test_duplicate_definition_identity(self):
        self.add_definition()
        other = dict(self.value['definitions'][0], local_id='other', position=1)
        self.value['definitions'].append(other)
        self.invalid('duplicate_definition')

    def test_cross_owner_parent(self):
        self.add_definition()
        self.value['nodes'][1]['definition_id'] = 'spell'
        self.invalid('cross_owner_parent')

    def test_reference_cycles_are_flat_links(self):
        self.add_definition()
        self.value['nodes'] += [node('support',owner='spell'),
            node('r1','reference','p',position=3,target_definition_local_id='spell'),
            node('r2','reference','support',owner='spell',target_definition_local_id='spell')]
        validate_snapshot(self.value)

    def test_unknown_and_missing_references(self):
        self.value['nodes'].append(node('r','reference','p',position=3,target_definition_local_id='absent'))
        self.invalid('unknown_reference')
        self.value['nodes'][-1].pop('target_definition_local_id')
        self.invalid('missing_reference_target')

    def test_urls(self):
        self.value['nodes'].append(node('l','link','p',position=3,url='https://example.org/rules#x'))
        validate_snapshot(self.value)
        for url in ('javascript:alert(1)', 'http://example.org', '//example.org', 'https://u:p@example.org',
                    'https://example.org:bad', 'https://example.org/a b', 'https://example.org/\nfoo', 'https://example.org:0'):
            self.value['nodes'][-1]['url'] = url
            self.invalid('unsafe_url')

    def test_partial_requires_warning(self):
        self.value['completeness'] = 'partial'
        self.invalid('partial_without_warning')
        self.value['warnings'] = [dict(position=0, code='unresolved', message='Unavailable definition')]
        validate_snapshot(self.value)

    def test_provenance_and_credits(self):
        p = self.value['provenance'][0]
        p['credits'] = [dict(position=0, attribution='Publisher',license_url='https://example.org/license')]
        validate_snapshot(self.value)
        p['credits'][0]['license_url'] = 'data:example'
        self.invalid('unsafe_url')
        p['credits'] = []
        self.value['provenance'].append(copy.deepcopy(p))
        self.invalid('duplicate_position')

    def test_selected_provenance_required(self):
        self.value['provenance'] = []
        self.invalid('invalid_selected_provenance')

    def test_metadata_and_digest_verification(self):
        digest = content_digest(self.value)
        self.value.update(revision=3,prepared_at='2026-11-15T10:00:00Z',content_digest=digest)
        validate_snapshot(self.value)
        self.assertEqual(content_digest(self.value),digest)
        self.value['nodes'][1]['text'] = 'Different '
        self.invalid('digest_mismatch')

    def test_invalid_metadata(self):
        for value in (True,0,-1,'1'):
            v=sample();v['revision']=value
            self.invalid('invalid_integer',v)
        for value in ('2026-11-15Z','2026-13-15T10:00:00Z','2026-11-15T10:00:00+00:00'):
            v=sample();v['prepared_at']=value
            self.invalid('invalid_timestamp',v)

    def test_digest_is_order_and_local_id_independent(self):
        self.add_definition('first')
        self.value['nodes'] += [node('defp',owner='first'),
            node('ref','reference','p',position=3,target_definition_local_id='first')]
        other=copy.deepcopy(self.value)
        other['definitions'][0]['local_id']='renamed'
        for n in other['nodes']:
            n['local_id']='new-'+n['local_id']
            if n['parent_local_id'] is not None:n['parent_local_id']='new-'+n['parent_local_id']
            if n['definition_id']=='first':n['definition_id']='renamed'
            if n.get('target_definition_local_id')=='first':n['target_definition_local_id']='renamed'
        other['nodes'].reverse()
        self.assertEqual(content_digest(self.value),content_digest(other))
        self.assertEqual(canonical_bytes(self.value),canonical_bytes(other))

    def test_content_changes_digest_and_input_is_unchanged(self):
        before=copy.deepcopy(self.value)
        digest=content_digest(self.value)
        self.assertEqual(self.value,before)
        self.value['source_label']='Another original source label'
        self.assertNotEqual(content_digest(self.value),digest)

    def test_facts_and_integer_types(self):
        self.value['facts']=[dict(position=0,key='str',label='STR',display_text='18 (+4)',integer_value=18)]
        validate_snapshot(self.value)
        self.value['facts'][0]['integer_value']=True
        self.invalid('invalid_integer')

    def test_sg_facts_are_only_allowed_on_related_definitions(self):
        self.value['facts'] = [dict(position=0,key='ac',label='AC',display_text='16',integer_value=16)]
        self.invalid('sg_owned_fact')
        self.add_definition()
        self.value['facts'][0]['definition_id']='spell'
        validate_snapshot(self.value)

    def test_default_limits(self):
        limits=ModelLimits()
        self.assertEqual((limits.snapshot_bytes,limits.content_nodes,limits.content_depth,
            limits.text_value_bytes,limits.supporting_definitions),(2097152,16384,16,65536,256))

    def test_root_position_is_scoped_per_definition(self):
        self.add_definition()
        self.value['nodes'].append(node('support',owner='spell'))
        validate_snapshot(self.value,ModelLimits(content_depth=2))

    def test_no_import_execution(self):
        self.value['nodes'][1]['text']='<script>alert(1)</script> [MON]'
        v=validate_snapshot(self.value)
        self.assertEqual(v['nodes'][1]['text'],self.value['nodes'][1]['text'])


if __name__=='__main__':
    unittest.main()
