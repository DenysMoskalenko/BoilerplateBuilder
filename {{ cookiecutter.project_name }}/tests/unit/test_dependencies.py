from fastapi import FastAPI
import pytest
from starlette.applications import Starlette

from tests.dependencies import DepOverride, temporary_override, temporary_overrides


@pytest.mark.parametrize('parent_has_override', [False, True])
def test_temporary_overrides_restore_each_app_after_nested_exception(parent_has_override: bool) -> None:
    parent, child, sibling, grandchild = (FastAPI() for _ in range(4))
    parent.mount('/child', child)
    parent.mount('/sibling', sibling)
    parent.mount('/static', Starlette())
    child.mount('/grandchild', grandchild)

    def dependency() -> str:
        return 'original'

    def other_dependency() -> str:
        return 'other'

    def parent_override() -> str:
        return 'parent'

    def child_override() -> str:
        return 'child'

    def outer() -> str:
        return 'outer'

    def inner() -> str:
        return 'inner'

    if parent_has_override:
        parent.dependency_overrides[dependency] = parent_override
    child.dependency_overrides[dependency] = child_override
    sibling.dependency_overrides[other_dependency] = child_override
    grandchild.dependency_overrides[dependency] = child_override
    previous = {app: app.dependency_overrides.copy() for app in (parent, child, sibling, grandchild)}

    with pytest.raises(RuntimeError, match='endpoint failed'):
        with temporary_overrides(parent, [DepOverride(dependency=dependency, override=outer)]):
            for app in (parent, child, sibling):
                assert app.dependency_overrides[dependency] is outer
            with temporary_override(parent, dependency, inner):
                for app in (parent, child, sibling):
                    assert app.dependency_overrides[dependency] is inner
            for app in (parent, child, sibling):
                assert app.dependency_overrides[dependency] is outer
            assert grandchild.dependency_overrides == previous[grandchild]
            raise RuntimeError('endpoint failed')

    for app, overrides in previous.items():
        assert app.dependency_overrides == overrides
