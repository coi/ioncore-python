# useragent_bc.py

from __future__ import with_statement
import itertools
from pyke import contexts, pattern, bc_rule

pyke_version = '1.1.1'
compiler_version = 1

def user_authorization_check(rule, arg_patterns, arg_context):
  engine = rule.rule_base.engine
  patterns = rule.goal_arg_patterns()
  if len(arg_patterns) == len(patterns):
    context = contexts.bc_context(rule)
    try:
      if all(itertools.imap(lambda pat, arg:
                              pat.match_pattern(context, context,
                                                arg, arg_context),
                            patterns,
                            arg_patterns)):
        rule.rule_base.num_bc_rules_matched += 1
        with engine.prove('useragent_facts', 'role_map', context,
                          (rule.pattern(0),
                           rule.pattern(1),
                           rule.pattern(2),)) \
          as gen_1:
          for x_1 in gen_1:
            assert x_1 is None, \
              "useragent.user_authorization_check: got unexpected plan from when clause 1"
            rule.rule_base.num_bc_rule_successes += 1
            yield
        rule.rule_base.num_bc_rule_failures += 1
    finally:
      context.done()

def populate(engine):
  This_rule_base = engine.get_create('useragent')
  
  bc_rule.bc_rule('user_authorization_check', This_rule_base, 'authorized_user',
                  user_authorization_check, None,
                  (contexts.variable('org'),
                   contexts.variable('user_id'),
                   contexts.variable('role'),),
                  (),
                  (contexts.variable('org'),
                   contexts.variable('role'),
                   contexts.variable('user_id'),))


Krb_filename = '../useragent.krb'
Krb_lineno_map = (
    ((16, 20), (6, 6)),
    ((22, 29), (8, 8)),
)
