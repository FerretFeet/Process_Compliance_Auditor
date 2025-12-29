from core.rules_engine.rule_builder.rule_builder import RuleBuilder

rule1 = RuleBuilder().define("Cpu Percent", "Cpu usage is above percentage value")\
    .source('process')\
    .when('cpu.percent > 60')\
    .then(lambda x: print('Rule 1 Failed'))

rule2 = RuleBuilder().define("Cpu Percent", "Cpu usage is below percentage value")\
    .source('process')\
    .when('cpu.percent < 60')\
    .then(lambda x: print('Rule 2 Failed'))

rule3 = RuleBuilder().define("memory percent and cpu percent", "Cpu usage and memory usage are below percentage value")\
    .source('process')\
    .when('cpu.percent < 60')\
    .and_('memory.percent < 60')\
    .then(lambda x: print('Rule 1 Failed'))

rule4 = RuleBuilder().define("memory percent and cpu percent 2", "Cpu usage below memory usage above")\
    .source('process')\
    .when('cpu.percent < 60')\
    .and_('memory.percent > 60')\
    .then(lambda x: print('Rule 1 Failed'))

