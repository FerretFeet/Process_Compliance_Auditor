from shared._common.operators import OPERATOR_FN, Operator


class TestOperatorMapping:
    def test_all_enum_members_have_function(self):
        """Assert that each Operator enum has a corresponding function in OPERATOR_FN."""
        missing = [op.value for op in Operator if op not in OPERATOR_FN]
        assert not missing, f"Missing operator functions for: {missing}"