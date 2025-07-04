#
# SPDX-FileCopyrightText: 2023 Univention GmbH
# SPDX-License-Identifier: AGPL-3.0-only

import inspect
import itertools
from pathlib import Path

import pytest
from pytestarch import EvaluableArchitecture, LayerRule, LayeredArchitecture, Rule, get_evaluable_architecture

import univention.scim.server


@pytest.fixture(scope="session")
def architecture() -> LayeredArchitecture:
    """
    Define "layers" for us with "Layer architecture rules".
    -> https://zyskarch.github.io/pytestarch/latest/features/layer_architecture_checks/

    Our "layers" are the components of the SCIM server.

    Unfortunately I didn't get `have_modules_with_names_matching()` to work.
    So I couldn't split "repo", "repo.udm", and "rules" from "domain".
    """
    return (
        LayeredArchitecture()
        .layer("authn")
        .containing_modules(["univention.scim.server.authn"])
        .layer("authz")
        .containing_modules(["univention.scim.server.authz"])
        .layer("domain")
        .containing_modules(["univention.scim.server.domain"])  # have_modules_with_names_matching() doesn't work for me
        .layer("model_service")  # or we could split "repo", "repo.udm", and "rules" from "domain".
        .containing_modules(["univention.scim.server.model_service"])
        .layer("rest")
        .containing_modules(["univention.scim.server.main", "univention.scim.server.rest"])
        .layer("transformation")
        .containing_modules(["univention.scim.transformation"])
    )


@pytest.fixture(scope="session")
def base_path() -> Path:
    """
    Will return the absolute path for .../scim-services/scim-server/src/univention ,
    so we can use full Python paths: "univention.scim.server...."
    """
    return Path(inspect.getsourcefile(univention.scim.server)).parent.parent.parent  # type: ignore


@pytest.fixture(scope="session")
def evaluable(base_path: Path) -> EvaluableArchitecture:
    """
    Generate the graph of Python module imports for use with "Module Dependency Rules".
    -> https://zyskarch.github.io/pytestarch/latest/features/module_import_checks/
    """
    assert str(base_path).endswith("univention")
    return get_evaluable_architecture(str(base_path), str(base_path), exclude_external_libraries=False)


@pytest.mark.parametrize(
    ["importer", "imported"],
    [
        ("domain", "transformation"),
        ("rest", "domain"),
    ],
)
def test_what_layer_should_access(
    architecture: LayeredArchitecture, evaluable: EvaluableArchitecture, importer: str, imported: str
) -> None:
    """Test what "layers" should access other layers."""
    rule = (
        LayerRule()
        .based_on(architecture)
        .layers_that()
        .are_named(importer)
        .should()
        .access_layers_that()
        .are_named(imported)
    )
    rule.assert_applies(evaluable)


@pytest.mark.parametrize(
    ["importer", "imported"],
    list(itertools.product(["authn"], ["authz", "domain", "rest"]))
    + list(itertools.product(["authz"], ["authn", "domain", "model_service", "rest"]))
    + list(itertools.product(["domain"], ["authn", "authz", "rest"]))
    + list(itertools.product(["model_service"], ["authn", "authz", "domain", "rest"])),
)
def test_what_layer_should_not_access(
    architecture: LayeredArchitecture, evaluable: EvaluableArchitecture, importer: str, imported: str
) -> None:
    """Test what "layers" should NOT access other layers."""
    rule = (
        LayerRule()
        .based_on(architecture)
        .layers_that()
        .are_named(importer)
        .should_not()
        .access_layers_that()
        .are_named(imported)
    )
    rule.assert_applies(evaluable)


@pytest.mark.parametrize(
    ["importer", "imported"],
    itertools.permutations(
        ["univention.scim.server.authn", "univention.scim.server.authz", "univention.scim.server.domain.repo.udm"],
        2,
    ),
)
def test_adapters_dont_import_adapters(evaluable: EvaluableArchitecture, importer: str, imported: str) -> None:
    """
    Test that adapters (of ports) don't import other adapters.

    Adapters should be independent of each other, so they can be modified without affecting other parts.
    """
    rule = (
        Rule()
        .modules_that()
        .are_sub_modules_of(imported)
        .should_not()
        .be_imported_by_modules_that()
        .are_sub_modules_of(importer)
    )
    rule.assert_applies(evaluable)


def test_business_only_imports_business(evaluable: EvaluableArchitecture) -> None:
    """
    Test that the modules of the business layer only import modules of the business layer.

    This is a central concept from the Hexagonal and Clean architecture.
    """
    rule = (
        Rule()
        .modules_that()
        .have_name_matching(r"^univention\.scim\.server\.domain\.(crud_scim|group_*|user_*|repo.crud_*|rules\..*)")
        .should_not()
        .import_modules_that()
        .have_name_matching(r"^univention\.scim\.server\.(authn|authz|domain\.repo\.udm|model_service|rest)")
    )
    rule.assert_applies(evaluable)
